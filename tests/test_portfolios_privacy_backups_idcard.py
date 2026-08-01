import hashlib
import pytest
import json
import zipfile
from io import BytesIO
from datetime import datetime, timedelta
from app.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

from app import create_app
from app.models import (
    db, User, DeviceSession, PublicProfileSetting, BackupRecord, IDCardToken,
    Competition, CompetitionParticipation, Certificate, Enrollment, Course
)

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        admin = User(username='admin', email='admin@test.org', role='admin', status='approved', is_root_admin=True, is_first_login=False, onboarding_completed=True)
        admin.set_password('AdminPass123!')

        student = User(username='student', email='student@test.org', role='member', status='approved', is_first_login=False, onboarding_completed=True)
        student.set_password('StudentPass123!')

        db.session.add_all([admin, student])
        db.session.commit()

        s_admin = DeviceSession(user_id=admin.id, session_token='token_admin', session_token_hash=hashlib.sha256(b'token_admin').hexdigest(), ip_address='127.0.0.1', user_agent='TestAgent', is_active=True)
        s_student = DeviceSession(user_id=student.id, session_token='token_student', session_token_hash=hashlib.sha256(b'token_student').hexdigest(), ip_address='127.0.0.1', user_agent='TestAgent', is_active=True)

        db.session.add_all([s_admin, s_student])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_public_profile_opt_in_toggle(client, app):
    student_headers = {'Authorization': 'Bearer token_student'}

    # 1. Fetch public profile before enabling (should be 404)
    res = client.get('/api/profile/public/student')
    assert res.status_code == 404

    # 2. Toggle public profile on
    res = client.post('/api/profile/privacy', json={'is_public': True, 'show_activity_hours': True, 'show_certificates': True}, headers=student_headers)
    assert res.status_code == 200
    assert res.json['is_public'] is True

    # 3. Fetch public profile again (should be 200)
    res = client.get('/api/profile/public/student')
    assert res.status_code == 200
    assert res.json['user']['username'] == 'student'

def test_privacy_data_export(client, app):
    student_headers = {'Authorization': 'Bearer token_student'}

    res = client.get('/api/profile/export-my-data', headers=student_headers)
    assert res.status_code == 200
    assert res.mimetype == 'application/zip'

    # Read zip file contents
    with zipfile.ZipFile(BytesIO(res.data), 'r') as zf:
        assert 'profile_summary.json' in zf.namelist()
        data = json.loads(zf.read('profile_summary.json').decode('utf-8'))
        assert data['account']['username'] == 'student'

def test_account_deletion_request(client, app):
    student_headers = {'Authorization': 'Bearer token_student'}

    res = client.post('/api/profile/request-deletion', json={'reason': 'Moving to a new platform'}, headers=student_headers)
    assert res.status_code == 200
    assert res.json['status'] == 'pending_review'

def test_backup_create_and_prune(client, app):
    admin_headers = {'Authorization': 'Bearer token_admin'}

    # 1. Trigger manual backup
    res = client.post('/api/admin/backups/create', headers=admin_headers)
    assert res.status_code == 201
    assert 'filename' in res.json['backup']
    backup_id = res.json['backup']['id']

    # 2. List backups
    res = client.get('/api/admin/backups', headers=admin_headers)
    assert res.status_code == 200
    assert len(res.json['backups']) == 1

    # 3. Test scheduled backup Celery task retention pruning
    from app.services.celery_tasks import perform_database_backup
    # Seed 15 records
    for i in range(15):
        b = BackupRecord(filename=f"backup_test_{i}.zip", size_bytes=1000, type='scheduled')
        db.session.add(b)
    db.session.commit()

    perform_database_backup(app)
    assert BackupRecord.query.count() <= 14

def test_id_card_token_and_public_verification(client, app):
    student_headers = {'Authorization': 'Bearer token_student'}

    # 1. Fetch ID card
    res = client.get('/api/profile/id-card', headers=student_headers)
    assert res.status_code == 200
    token = res.json['token']
    assert len(token) == 64

    # 2. Public verification route (no auth header needed)
    res = client.get(f"/api/verify/{token}")
    assert res.status_code == 200
    assert res.json['member']['username'] == 'student'
    assert res.json['member']['member_id'] == 'HX-STU-0002'

    # 3. Regenerate token
    res = client.post('/api/profile/id-card/regenerate', headers=student_headers)
    assert res.status_code == 200
    new_token = res.json['token']
    assert new_token != token

    # Old token should now be 404 invalid
    res = client.get(f"/api/verify/{token}")
    assert res.status_code == 404

    # New token should be valid
    res = client.get(f"/api/verify/{new_token}")
    assert res.status_code == 200

def test_portfolio_pdf_export(client, app):
    student_headers = {'Authorization': 'Bearer token_student'}

    res = client.get('/api/portfolio/export-pdf', headers=student_headers)
    assert res.status_code == 200
    assert 'application/pdf' in res.mimetype or 'pdf' in res.headers.get('Content-Disposition', '')
