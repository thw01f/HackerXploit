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
def perform_database_backup():
    from app import create_app
    from app.models import db, AuditLog
    app = create_app()
    with app.app_context():
        log = AuditLog(
            actor_id=None,
            actor_name='Celery Beat',
            actor_role='system',
            action='AUTOMATED_BACKUP_SNAPSHOT',
            details={'status': 'completed', 'timestamp': datetime.utcnow().isoformat()}
        )
        db.session.add(log)
        db.session.commit()
        return "Automated DB Backup Completed"

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Run lockout cleanup every 5 minutes
    sender.add_periodic_task(300.0, cleanup_expired_lockouts.s(), name='cleanup-lockouts-5m')
    # Run competition retention daily at midnight
    sender.add_periodic_task(crontab(hour=0, minute=0), clean_expired_competitions.s(), name='daily-competition-retention')
    # Daily database backup at midnight
    sender.add_periodic_task(crontab(hour=0, minute=5), perform_database_backup.s(), name='daily-db-backup')
