import hashlib
import pytest
from datetime import datetime
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
    db, User, DeviceSession, Notification, ChatMessage, Message, MessageRecipient,
    Report, SiteFeatureToggle, EmailLog
)

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        admin = User(username='admin', email='admin@test.org', role='admin', status='approved', is_root_admin=True, is_first_login=False, onboarding_completed=True)
        admin.set_password('AdminPass123!')

        teacher = User(username='teacher', email='teacher@test.org', role='teacher', status='approved', is_first_login=False, onboarding_completed=True)
        teacher.set_password('TeacherPass123!')

        student = User(username='student', email='student@test.org', role='member', status='approved', is_first_login=False, onboarding_completed=True)
        student.set_password('StudentPass123!')

        db.session.add_all([admin, teacher, student])
        db.session.commit()

        s_admin = DeviceSession(user_id=admin.id, session_token='token_admin', session_token_hash=hashlib.sha256(b'token_admin').hexdigest(), ip_address='127.0.0.1', user_agent='TestAgent', is_active=True)
        s_teacher = DeviceSession(user_id=teacher.id, session_token='token_teacher', session_token_hash=hashlib.sha256(b'token_teacher').hexdigest(), ip_address='127.0.0.1', user_agent='TestAgent', is_active=True)
        s_student = DeviceSession(user_id=student.id, session_token='token_student', session_token_hash=hashlib.sha256(b'token_student').hexdigest(), ip_address='127.0.0.1', user_agent='TestAgent', is_active=True)

        db.session.add_all([s_admin, s_teacher, s_student])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_notifications_api(client, app):
    student_headers = {'Authorization': 'Bearer token_student'}
    student = User.query.filter_by(username='student').first()

    # Create dummy notification
    n = Notification(user_id=student.id, title="Test Notif", message="Welcome to the platform", type="system")
    db.session.add(n)
    db.session.commit()

    # Fetch notifications
    res = client.get('/api/notifications', headers=student_headers)
    assert res.status_code == 200
    assert len(res.json['notifications']) == 1
    assert res.json['unread_count'] == 1

    # Mark single read
    res = client.put(f"/api/notifications/{n.id}/read", headers=student_headers)
    assert res.status_code == 200
    assert res.json['is_read'] is True

    # Mark all read
    res = client.post('/api/notifications/read-all', headers=student_headers)
    assert res.status_code == 200

def test_text_chat_and_moderation(client, app):
    student_headers = {'Authorization': 'Bearer token_student'}
    teacher_headers = {'Authorization': 'Bearer token_teacher'}
    admin_headers = {'Authorization': 'Bearer token_admin'}

    # 1. Student posts message
    res = client.post('/api/chat/messages', json={'channel': 'general', 'content': 'Hello world text only!'}, headers=student_headers)
    assert res.status_code == 201
    msg_id = res.json['id']

    # 2. Teacher soft-deletes message
    res = client.delete(f"/api/chat/messages/{msg_id}", headers=teacher_headers)
    assert res.status_code == 200
    assert "Message deleted by teacher" in res.json['chat_message']['content']

    # 3. Student files report on another chat message
    res2 = client.post('/api/chat/messages', json={'channel': 'general', 'content': 'Inappropriate text message'}, headers=student_headers)
    msg2_id = res2.json['id']

    res = client.post(f"/api/chat/messages/{msg2_id}/report", json={'reason': 'Inappropriate language'}, headers=student_headers)
    assert res.status_code == 201
    assert res.json['report']['target_id'] == msg2_id

    # 4. Admin performs room hard-reset
    res = client.post('/api/chat/reset', json={'channel': 'general'}, headers=admin_headers)
    assert res.status_code == 200
    assert ChatMessage.query.count() == 0

def test_broadcast_inbox_and_recipient_actions(client, app):
    teacher_headers = {'Authorization': 'Bearer token_teacher'}
    student_headers = {'Authorization': 'Bearer token_student'}

    # 1. Teacher composes broadcast message to all members
    res = client.post('/api/inbox/messages', json={
        'subject': 'Welcome Assembly',
        'body': 'Join us at 5 PM in room 302.',
        'scope': 'all_members',
        'allow_reply': True
    }, headers=teacher_headers)
    assert res.status_code == 201
    assert res.json['recipient_count'] >= 3

    # 2. Student fetches inbox
    res = client.get('/api/inbox', headers=student_headers)
    assert res.status_code == 200
    inbox = res.json['inbox']
    assert len(inbox) >= 1
    target = inbox[0]
    rec_id = target['recipient_id']

    # 3. Mark message read & archive
    res = client.put(f"/api/inbox/recipients/{rec_id}/read", headers=student_headers)
    assert res.status_code == 200
    assert res.json['is_read'] is True

    res = client.put(f"/api/inbox/recipients/{rec_id}/archive", headers=student_headers)
    assert res.status_code == 200
    assert res.json['is_archived'] is True

    # 4. Student replies to message
    res = client.post(f"/api/inbox/{target['message_id']}/reply", json={'body': 'I will be there!'}, headers=student_headers)
    assert res.status_code == 201

    # 5. Delete from my inbox
    res = client.delete(f"/api/inbox/recipients/{rec_id}", headers=student_headers)
    assert res.status_code == 200

def test_admin_inbox_logs(client, app):
    teacher_headers = {'Authorization': 'Bearer token_teacher'}
    admin_headers = {'Authorization': 'Bearer token_admin'}

    # Send message
    client.post('/api/inbox/messages', json={
        'subject': 'Important Update',
        'body': 'Please review your project submissions.',
        'scope': 'all_members'
    }, headers=teacher_headers)

    # Fetch admin log
    res = client.get('/api/inbox/admin/log', headers=admin_headers)
    assert res.status_code == 200
    assert len(res.json['inbox_logs']) >= 1

def test_unified_moderation_queue(client, app):
    admin_headers = {'Authorization': 'Bearer token_admin'}
    student = User.query.filter_by(username='student').first()

    # Create dummy report
    rep = Report(reported_by_id=student.id, target_type='chat_message', target_id=1, reason='Spam content')
    db.session.add(rep)
    db.session.commit()

    # Fetch moderation queue
    res = client.get('/api/admin/reports?status=pending', headers=admin_headers)
    assert res.status_code == 200
    assert len(res.json['reports']) >= 1

    # Resolve report
    res = client.post(f"/api/admin/reports/{rep.id}/resolve", headers=admin_headers)
    assert res.status_code == 200
    assert res.json['resolved'] is True

def test_site_feature_toggles(client, app):
    admin_headers = {'Authorization': 'Bearer token_admin'}
    student_headers = {'Authorization': 'Bearer token_student'}

    # 1. Fetch settings
    res = client.get('/api/admin/settings', headers=admin_headers)
    assert res.status_code == 200
    assert res.json['general_chat_enabled'] is True

    # 2. Disable general chat
    res = client.post('/api/admin/settings', json={'general_chat_enabled': False}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json['general_chat_enabled'] is False

    # 3. Verify student gets 403 when trying to post chat message
    res = client.post('/api/chat/messages', json={'channel': 'general', 'content': 'Test when disabled'}, headers=student_headers)
    assert res.status_code == 403
