import hashlib
import pytest
from app.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'

from app import create_app
from app.models import db, User, DeviceSession, Announcement

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        admin = User(username='admin', email='admin@test.com', role='admin', status='approved', is_root_admin=True, is_first_login=False, onboarding_completed=True)
        admin.set_password('Password123!')
        student = User(username='student', email='student@test.com', role='member', status='approved', is_first_login=False, onboarding_completed=True)
        student.set_password('Password123!')

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


def test_announcement_crud_and_visibility(client, app):
    headers_admin = {'Authorization': 'Bearer token_admin'}
    headers_student = {'Authorization': 'Bearer token_student'}

    # Student cannot manage announcements
    res_forbidden = client.get('/api/admin/announcements', headers=headers_student)
    assert res_forbidden.status_code == 403

    # Link requires a button label
    res_bad = client.post('/api/admin/announcements', json={
        'message': 'Missing label test',
        'link': 'https://arena.hackerxploit.org'
    }, headers=headers_admin)
    assert res_bad.status_code == 400

    # Create with CTA
    res_create = client.post('/api/admin/announcements', json={
        'message': 'Next CTF competition is scheduled for Saturday.',
        'button_label': 'LAUNCH CTF ARENA',
        'link': 'https://arena.hackerxploit.org'
    }, headers=headers_admin)
    assert res_create.status_code == 201
    ann_id = res_create.json['id']
    assert res_create.json['is_active'] is True

    # Create a plain-text announcement (no CTA)
    res_create2 = client.post('/api/admin/announcements', json={'message': 'Second announcement, no button'}, headers=headers_admin)
    assert res_create2.status_code == 201
    ann_id2 = res_create2.json['id']

    # Both show up in the public active feed, for a regular student
    res_active = client.get('/api/announcements/active', headers=headers_student)
    assert res_active.status_code == 200
    assert len(res_active.json['announcements']) == 2

    # Deactivate the first one
    res_update = client.put(f'/api/admin/announcements/{ann_id}', json={'is_active': False}, headers=headers_admin)
    assert res_update.status_code == 200
    assert res_update.json['is_active'] is False

    res_active2 = client.get('/api/announcements/active', headers=headers_student)
    assert len(res_active2.json['announcements']) == 1
    assert res_active2.json['announcements'][0]['id'] == ann_id2

    # Admin list still shows both regardless of active state
    res_list = client.get('/api/admin/announcements', headers=headers_admin)
    assert len(res_list.json['announcements']) == 2

    # Delete
    res_delete = client.delete(f'/api/admin/announcements/{ann_id2}', headers=headers_admin)
    assert res_delete.status_code == 200
    assert Announcement.query.count() == 1
