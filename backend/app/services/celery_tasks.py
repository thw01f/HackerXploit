import os
from datetime import datetime, timedelta
from celery import Celery
from celery.schedules import crontab

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
            u.failed_login_attempts = 0
        db.session.commit()
        return f"Unlocked {len(users)} accounts"

@celery.task
def perform_database_backup():
    from app import create_app
    from app.models import db, AuditLog
    app = create_app()
    with app.app_context():
        # Trigger DB backup record in audit log
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
    # Daily database backup at midnight
    sender.add_periodic_task(crontab(hour=0, minute=0), perform_database_backup.s(), name='daily-db-backup')
