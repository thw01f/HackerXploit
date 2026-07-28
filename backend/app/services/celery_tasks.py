import os
from datetime import datetime, timedelta
from celery import Celery
from celery.schedules import crontab
from flask import has_app_context

def make_celery(app_name=__name__):
    redis_url = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
    celery = Celery(app_name, broker=redis_url, backend=redis_url)
    return celery

celery = make_celery()

@celery.task
def cleanup_expired_lockouts():
    from app import create_app
    from app.models import db, User
    app = create_app()
    with app.app_context():
        now = datetime.utcnow()
        users = User.query.filter(User.locked_until <= now).all()
        for u in users:
            u.locked_until = None
            u.failed_login_count = 0
        db.session.commit()
        return f"Unlocked {len(users)} accounts"

@celery.task
def clean_expired_competitions(app=None):
    from app import create_app
    from app.models import db, Competition, RetentionSettings

    def _run():
        settings = RetentionSettings.query.first()
        if not settings or settings.competitions_auto_delete == 'never':
            return "No auto-delete active"

        days_map = {'1_month': 30, '3_month': 90, '6_month': 180}
        days = days_map.get(settings.competitions_auto_delete, 30)
        cutoff = datetime.utcnow() - timedelta(days=days)

        expired_comps = Competition.query.filter(
            Competition.status == 'ended',
            Competition.ends_at <= cutoff,
            Competition.is_archived == False
        ).all()

        count = len(expired_comps)
        for comp in expired_comps:
            if settings.competitions_delete_mode == 'hard_delete':
                db.session.delete(comp)
            else:
                comp.is_archived = True

        db.session.commit()
        return f"Processed {count} expired competitions with mode '{settings.competitions_delete_mode}'"

    if has_app_context():
        return _run()
    else:
        app_inst = app if app else create_app()
        with app_inst.app_context():
            return _run()

@celery.task
def rollup_activity_heartbeats(app=None):
    """Nightly Celery job rolls raw heartbeats into activity_sessions duration, then prunes raw rows"""
    from app import create_app
    from app.models import db, ActivityHeartbeat, ActivitySession

    def _run():
        heartbeats = ActivityHeartbeat.query.order_by(ActivityHeartbeat.ts.asc()).all()
        if not heartbeats:
            return "No raw heartbeats to rollup"

        processed_ids = []
        user_date_map = {}

        for hb in heartbeats:
            processed_ids.append(hb.id)
            d_str = hb.ts.strftime('%Y-%m-%d')
            key = (hb.user_id, d_str, hb.subdomain)

            if key not in user_date_map:
                user_date_map[key] = {
                    'count': 0,
                    'first_ts': hb.ts,
                    'last_ts': hb.ts
                }

            user_date_map[key]['count'] += 1
            user_date_map[key]['last_ts'] = hb.ts

        # Upsert into ActivitySession (each heartbeat ping ~ 60s active duration)
        for (u_id, d_str, sub), info in user_date_map.items():
            sess = ActivitySession.query.filter_by(user_id=u_id, date=d_str, subdomain=sub).first()
            duration = info['count'] * 60

            if not sess:
                sess = ActivitySession(
                    user_id=u_id,
                    date=d_str,
                    subdomain=sub,
                    login_at=info['first_ts'],
                    logout_at=info['last_ts'],
                    duration_seconds=duration
                )
                db.session.add(sess)
            else:
                sess.duration_seconds += duration
                sess.logout_at = info['last_ts']

        # Prune processed raw heartbeat rows
        ActivityHeartbeat.query.filter(ActivityHeartbeat.id.in_(processed_ids)).delete(synchronize_session=False)
        db.session.commit()
        return f"Rolled up {len(processed_ids)} heartbeats into {len(user_date_map)} activity sessions"

    if has_app_context():
        return _run()
    else:
        app_inst = app if app else create_app()
        with app_inst.app_context():
            return _run()

@celery.task
def recalculate_leaderboard(app=None):
    """Nightly Celery job recalculating weighted leaderboard scores"""
    from app import create_app
    from app.models import db, User, CompetitionParticipation, Enrollment

    def _run():
        users = User.query.filter_by(status='approved').all()
        for u in users:
            # Weighted formula: Wins=100, RunnerUp=50, Participated=15, CourseCompleted=30
            wins = CompetitionParticipation.query.filter_by(user_id=u.id, result='winner').count()
            runners = CompetitionParticipation.query.filter_by(user_id=u.id, result='runner_up').count()
            parts = CompetitionParticipation.query.filter_by(user_id=u.id, result='participated').count()
            completed_courses = Enrollment.query.filter_by(user_id=u.id, progress_percent=100.0).count()

            score = (wins * 100.0) + (runners * 50.0) + (parts * 15.0) + (completed_courses * 30.0)
            u.leaderboard_score = score

        db.session.commit()
        return f"Recalculated leaderboard scores for {len(users)} users"

    if has_app_context():
        return _run()
    else:
        app_inst = app if app else create_app()
        with app_inst.app_context():
            return _run()

@celery.task
def perform_database_backup(app=None):
    from app import create_app
    from app.models import db, BackupRecord, AuditLog
    from app.routes.backups import create_backup_archive

    def _run():
        record, checksum = create_backup_archive(created_by_id=None, backup_type='scheduled')

        # Keep last 14 backups, prune older
        backups = BackupRecord.query.order_by(BackupRecord.created_at.desc()).all()
        if len(backups) > 14:
            old_backups = backups[14:]
            for b in old_backups:
                db.session.delete(b)
            db.session.commit()

        log = AuditLog(
            actor_id=None,
            actor_name='Celery Beat',
            actor_role='system',
            action='AUTOMATED_BACKUP_SNAPSHOT',
            notes=f"Created backup {record.filename}. Total records kept: {min(len(backups), 14)}"
        )
        db.session.add(log)
        db.session.commit()
        return f"Automated Scheduled Backup Completed: {record.filename}"

    if has_app_context():
        return _run()
    else:
        app_inst = app if app else create_app()
        with app_inst.app_context():
            return _run()


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Run lockout cleanup every 5 minutes
    sender.add_periodic_task(300.0, cleanup_expired_lockouts.s(), name='cleanup-lockouts-5m')
    # Run competition retention daily at midnight
    sender.add_periodic_task(crontab(hour=0, minute=0), clean_expired_competitions.s(), name='daily-competition-retention')
    # Run activity rollup daily at 00:15
    sender.add_periodic_task(crontab(hour=0, minute=15), rollup_activity_heartbeats.s(), name='daily-activity-rollup')
    # Run leaderboard recalculation daily at 00:30
    sender.add_periodic_task(crontab(hour=0, minute=30), recalculate_leaderboard.s(), name='daily-leaderboard-recalc')
    # Daily database backup at midnight
    sender.add_periodic_task(crontab(hour=0, minute=5), perform_database_backup.s(), name='daily-db-backup')
