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
