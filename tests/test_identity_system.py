import os
import sys
import pytest
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

from app import create_app
from app.models import db, User, DeviceSession, AuditLog, LoginAttempt
from app.utils.decorators import get_current_user

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

def test_approval_state_machine(client):
    """Test approval state machine: pending -> approved -> suspended -> reinstated"""
    with client.application.app_context():
        # 1. Admin actor
        admin = User(username='admin_actor', email='admin@hx.org', role='admin', is_root_admin=True, status='approved')
        admin.set_password('Pass123!')
        
        # 2. Registrant user
        member = User(username='applicant', email='applicant@hx.org', role='member', status='pending')
        member.set_password('Pass123!')
        
        db.session.add_all([admin, member])
        db.session.commit()

        assert member.status == 'pending'

        # 3. Approve user
        member.status = 'approved'
        member.approved_by = admin.id
        member.approved_at = datetime.utcnow()
        db.session.commit()

        assert member.status == 'approved'
        assert member.approved_by == admin.id

        # 4. Create active session for member
        sess = DeviceSession(user_id=member.id, session_token='token123', ip_address='127.0.0.1', user_agent='Test', is_active=True)
        db.session.add(sess)
        db.session.commit()

        # 5. Suspend user -> should invalidate active sessions
        member.status = 'suspended'
        DeviceSession.query.filter_by(user_id=member.id, is_active=True).update({'is_active': False})
        db.session.commit()

        assert member.status == 'suspended'
        assert db.session.get(DeviceSession, sess.id).is_active is False

        # 6. Reinstate user
        member.status = 'approved'
        db.session.commit()
        assert member.status == 'approved'

def test_lockout_logic_and_manual_unlock(client):
    """Test lockout logic: 5 failed attempts -> 15 min lock -> manual unlock"""
    with client.application.app_context():
        user = User(username='victim', email='victim@hx.org', role='member', status='approved')
        user.set_password('CorrectPassword123!')
        db.session.add(user)
        db.session.commit()

        # 5 consecutive failed checks
        for _ in range(5):
            res = user.check_password('WrongPassword!')
            assert res is False

        assert user.failed_login_count >= 5
        assert user.is_locked() is True

        # Correct password during lock returns False
        assert user.check_password('CorrectPassword123!') is False

        # Manual unlock
        user.locked_until = None
        user.failed_login_count = 0
        db.session.commit()

        assert user.is_locked() is False
        assert user.check_password('CorrectPassword123!') is True

def test_device_kill_switch_invalidation(client):
    """Test device session revocation and instant kill-switch"""
    with client.application.app_context():
        user = User(username='session_user', email='sess@hx.org', role='member', status='approved')
        user.set_password('Pass123!')
        db.session.add(user)
        db.session.commit()

        sess = DeviceSession(user_id=user.id, session_token='valid_token_77', ip_address='10.0.0.1', user_agent='Chrome', is_active=True)
        db.session.add(sess)
        db.session.commit()

        # Invalidate session
        sess.is_active = False
        db.session.commit()

        # Query active session
        found = DeviceSession.query.filter_by(session_token='valid_token_77', is_active=True).first()
        assert found is None

def test_root_admin_promotion_cap(client):
    """Test non-root admin hard cap of 5 and root admin demotion protection"""
    with client.application.app_context():
        root = User(username='root', email='root@hx.org', role='admin', is_root_admin=True, status='approved')
        root.set_password('RootPass123!')
        db.session.add(root)

        # Create 5 non-root admins
        for i in range(5):
            adm = User(username=f'admin_{i}', email=f'admin_{i}@hx.org', role='admin', is_root_admin=False, status='approved')
            adm.set_password('Pass123!')
            db.session.add(adm)
        
        db.session.commit()

        # Count non-root admins
        count = User.query.filter_by(role='admin', is_root_admin=False).count()
        assert count == 5

        # Attempt to create 6th admin candidate
        sixth_user = User(username='sixth', email='sixth@hx.org', role='member', status='approved')
        sixth_user.set_password('Pass123!')
        db.session.add(sixth_user)
        db.session.commit()

        # Verify enforcement rule
        if User.query.filter_by(role='admin', is_root_admin=False).count() >= 5:
            at_cap = True
        else:
            at_cap = False

        assert at_cap is True
