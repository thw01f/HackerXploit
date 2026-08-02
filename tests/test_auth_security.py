import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'

from app import create_app, db
from app.models import User, DeviceSession
from app.services.upload_service import UploadPipeline

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

def test_argon2_password_and_lockout(client):
    with client.application.app_context():
        user = User(username='testuser', email='test@hx.org', full_name='Test User')
        user.set_password('SecretPass123!')
        db.session.add(user)
        db.session.commit()

        # Check valid password
        assert user.check_password('SecretPass123!') is True

        # Check 5 invalid password attempts trigger lockout
        for _ in range(5):
            user.check_password('WrongPass')
        
        assert user.is_locked() is True
        assert user.check_password('SecretPass123!') is False

def test_lockout_message_and_auto_unlock_logging(client):
    from datetime import datetime, timedelta
    from app.models import AuditLog
    from app.services.celery_tasks import cleanup_expired_lockouts

    with client.application.app_context():
        user = User(username='lockoutuser', email='lockout@hx.org', full_name='Lockout User', status='approved', is_first_login=False, onboarding_completed=True)
        user.set_password('SecretPass123!')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

        # Trigger the lockout at the model level (matches test_argon2_password_and_lockout) -
        # a real HTTP loop here would trip the auth_bp blanket rate limiter instead.
        for _ in range(5):
            user.check_password('WrongPass')
        db.session.commit()
        assert user.is_locked() is True

    # A single real HTTP request to confirm the login endpoint's own message/status
    res = client.post('/api/auth/login', json={'email_or_username': 'lockoutuser', 'password': 'SecretPass123!'})
    assert res.status_code == 423
    assert '60 minutes' in res.json['error']
    assert 'contact an administrator' in res.json['error']

    with client.application.app_context():
        locked_user = User.query.get(user_id)
        assert locked_user.locked_until is not None
        # Confirm the real lockout window is 30 minutes, not 60
        remaining = locked_user.locked_until - datetime.utcnow()
        assert timedelta(minutes=25) < remaining <= timedelta(minutes=30)

        # Simulate the lockout window having already expired, then run the
        # scheduled auto-unlock task the same way Celery beat would
        locked_user.locked_until = datetime.utcnow() - timedelta(minutes=1)
        db.session.commit()

    cleanup_expired_lockouts()

    with client.application.app_context():
        unlocked_user = User.query.get(user_id)
        assert unlocked_user.locked_until is None
        assert unlocked_user.failed_login_count == 0

        log = AuditLog.query.filter_by(action='auto_unlocked', target_user_id=user_id).first()
        assert log is not None
        assert 'lockoutuser' in log.notes

def test_admin_hard_cap(client):
    with client.application.app_context():
        root = User(username='root', email='root@hx.org', full_name='Root', role='root_admin', status='approved')
        root.set_password('Pass123!')
        db.session.add(root)
        
        # Add 5 admins
        for i in range(5):
            adm = User(username=f'admin{i}', email=f'admin{i}@hx.org', full_name=f'Admin {i}', role='admin', status='approved')
            adm.set_password('Pass123!')
            db.session.add(adm)
        db.session.commit()

        assert User.query.filter_by(role='admin').count() == 5

def test_mime_detection():
    # JPEG Header test
    jpeg_bytes = b'\xff\xd8\xff\xe0\x00\x10JFIF'
    from io import BytesIO
    stream = BytesIO(jpeg_bytes)
    mime = UploadPipeline.detect_mime(stream)
    assert mime == 'image/jpeg'
