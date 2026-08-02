import hashlib
import pytest
from datetime import datetime, timedelta
from app.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'

from app import create_app
from app.models import db, User, DeviceSession, Competition, CompetitionParticipation, Certificate, RetentionSettings, Opportunity, Skill, member_skills, opportunity_skills
from app.services.celery_tasks import clean_expired_competitions

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        # Seed test users
        admin = User(username='admin', email='admin@test.com', role='admin', status='approved', is_root_admin=True, is_first_login=False, onboarding_completed=True)
        admin.set_password('Password123!')

        teacher = User(username='teacher', email='teacher@test.com', role='teacher', status='approved', is_first_login=False, onboarding_completed=True)
        teacher.set_password('Password123!')

        student = User(username='student', email='student@test.com', role='member', status='approved', is_first_login=False, onboarding_completed=True)
        student.set_password('Password123!')

        db.session.add_all([admin, teacher, student])
        db.session.commit()

        # Add active device sessions with user_agent
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

def test_competition_lifecycle_and_certificates(client, app):
    headers_teacher = {'Authorization': 'Bearer token_teacher'}
    headers_student = {'Authorization': 'Bearer token_student'}

    starts = (datetime.utcnow() - timedelta(days=2)).isoformat()
    ends = (datetime.utcnow() - timedelta(days=1)).isoformat()

    # 1. Announce competition
    res_create = client.post('/api/competitions', json={
        'title': 'National CTF Finals',
        'description': 'Jeopardy CTF Competition',
        'category': 'ctf',
        'priority': 'high',
        'starts_at': starts,
        'ends_at': ends,
        'external_link': 'https://ctf.org'
    }, headers=headers_teacher)
    assert res_create.status_code == 201
    comp_id = res_create.json['id']
    assert res_create.json['priority'] == 'high'

    # 2. Student applies with screenshot proof
    res_apply = client.post(f'/api/competitions/{comp_id}/apply', json={
        'application_screenshot': '/uploads/screenshots/proof.webp'
    }, headers=headers_student)
    assert res_apply.status_code == 201
    app_id = res_apply.json['id']
    assert res_apply.json['application_status'] == 'pending_verification'

    # 3. Teacher queue & verify application
    res_queue = client.get(f'/api/competitions/{comp_id}/applications', headers=headers_teacher)
    assert res_queue.status_code == 200
    assert len(res_queue.json['applications']) == 1

    res_verify = client.post(f'/api/competitions/{comp_id}/applications/{app_id}/verify', json={
        'status': 'verified'
    }, headers=headers_teacher)
    assert res_verify.status_code == 200
    assert res_verify.json['application_status'] == 'verified'

    # 4. Teacher post-event wrapup with Winner result -> Auto PDF Certificate
    res_wrapup = client.post(f'/api/competitions/{comp_id}/wrapup', json={
        'summary_notes': 'Secured 1st place in Jeopardy CTF',
        'participants': [
            {
                'participation_id': app_id,
                'result': 'winner',
                'placement_label': '1st Place Winner'
            }
        ]
    }, headers=headers_teacher)
    assert res_wrapup.status_code == 200
    assert res_wrapup.json['status'] == 'ended'

    # Check Certificate row created in DB
    cert = Certificate.query.filter_by(source_id=comp_id, type='competition').first()
    assert cert is not None

def test_competition_completion_report_flow(client, app):
    headers_teacher = {'Authorization': 'Bearer token_teacher'}
    headers_student = {'Authorization': 'Bearer token_student'}

    starts = (datetime.utcnow() - timedelta(days=2)).isoformat()
    ends = (datetime.utcnow() - timedelta(days=1)).isoformat()

    res_create = client.post('/api/competitions', json={
        'title': 'Regional Hackathon',
        'description': 'Build something in 24 hours',
        'category': 'hackathon',
        'starts_at': starts,
        'ends_at': ends,
    }, headers=headers_teacher)
    assert res_create.status_code == 201
    comp_id = res_create.json['id']

    # More than 3 registration screenshots must be rejected
    res_too_many = client.post(f'/api/competitions/{comp_id}/apply', json={
        'application_screenshots': ['/uploads/competitions/a.webp', '/uploads/competitions/b.webp',
                                     '/uploads/competitions/c.webp', '/uploads/competitions/d.webp']
    }, headers=headers_student)
    assert res_too_many.status_code == 400

    # Apply with 3 screenshots (max allowed)
    res_apply = client.post(f'/api/competitions/{comp_id}/apply', json={
        'application_screenshots': ['/uploads/competitions/a.webp', '/uploads/competitions/b.webp',
                                     '/uploads/competitions/c.webp']
    }, headers=headers_student)
    assert res_apply.status_code == 201
    app_id = res_apply.json['id']
    assert len(res_apply.json['application_screenshots']) == 3

    # Completion report blocked before staff verifies registration
    res_early = client.post(f'/api/competitions/{comp_id}/complete', json={
        'event_photos': ['/uploads/competitions/event1.webp'],
        'summary_notes': 'Too early',
    }, headers=headers_student)
    assert res_early.status_code == 403

    # Staff verifies the registration
    res_verify = client.post(f'/api/competitions/{comp_id}/applications/{app_id}/verify', json={
        'status': 'verified'
    }, headers=headers_teacher)
    assert res_verify.status_code == 200

    # Now the student can file their post-event completion report
    res_complete = client.post(f'/api/competitions/{comp_id}/complete', json={
        'event_photos': ['/uploads/competitions/event1.webp', '/uploads/competitions/event2.webp'],
        'summary_notes': 'Built a phishing detector, learned about DNS.',
        'github_link': 'https://github.com/student/phish-detector',
        'prize_money': '₹5,000',
        'self_reported_result': 'winner',
    }, headers=headers_student)
    assert res_complete.status_code == 200
    assert res_complete.json['completion_status'] == 'pending_review'
    assert res_complete.json['github_link'] == 'https://github.com/student/phish-detector'
    # Registration proof is superseded and cleared once completion is filed
    assert res_complete.json['application_screenshots'] == []

    # More than 5 event photos must be rejected
    res_too_many_photos = client.post(f'/api/competitions/{comp_id}/complete', json={
        'event_photos': ['/uploads/competitions/e1.webp'] * 6,
    }, headers=headers_student)
    assert res_too_many_photos.status_code == 400

    # Staff finalizes via wrap-up, which should promote completion_status to 'verified'
    # and honor the student's self-reported result as a default when staff doesn't override it.
    res_wrapup = client.post(f'/api/competitions/{comp_id}/wrapup', json={
        'participants': [
            {'participation_id': app_id, 'placement_label': '1st Place'}
        ]
    }, headers=headers_teacher)
    assert res_wrapup.status_code == 200

    part = CompetitionParticipation.query.get(app_id)
    assert part.completion_status == 'verified'
    assert part.result == 'winner'
    # Staff didn't submit event_photos in wrapup - the student's own photos must survive untouched
    assert len(part.event_photos) == 2


def test_retention_celery_beat_task(client, app):
    headers_admin = {'Authorization': 'Bearer token_admin'}

    res_retention = client.post('/api/admin/retention', json={
        'competitions_auto_delete': '1_month',
        'competitions_delete_mode': 'archive'
    }, headers=headers_admin)
    assert res_retention.status_code == 200

    # Create an old ended competition (ends 60 days ago)
    old_ends = datetime.utcnow() - timedelta(days=60)
    comp = Competition(
        title='Old CTF',
        description='Past CTF',
        starts_at=old_ends - timedelta(days=1),
        ends_at=old_ends,
        status='ended',
        is_archived=False
    )
    db.session.add(comp)
    db.session.commit()
    c_id = comp.id

    # Run Celery beat task directly passing app instance
    msg = clean_expired_competitions(app)
    assert "Processed 1 expired" in msg



    # Verify competition is archived
    updated_comp = Competition.query.get(c_id)
    assert updated_comp.is_archived is True

def test_skill_matched_opportunities(client, app):
    headers_student = {'Authorization': 'Bearer token_student'}
    headers_admin = {'Authorization': 'Bearer token_admin'}

    # 1. Create master skills
    s1 = Skill(name='Reverse Engineering')
    s2 = Skill(name='Web Exploitation')
    s3 = Skill(name='Cryptography')
    db.session.add_all([s1, s2, s3])
    db.session.commit()

    # 2. Assign skills to student (s1, s2)
    res_user_skills = client.post('/api/opportunities/user/skills', json={
        'skill_ids': [s1.id, s2.id]
    }, headers=headers_student)
    assert res_user_skills.status_code == 200

    # 3. Create opportunity with skills (s1, s2, s3)
    res_opp = client.post('/api/opportunities', json={
        'title': 'Binary Exploitation Specialist',
        'company': 'CyberFirm',
        'type': 'job',
        'description': 'Senior Vulnerability Researcher',
        'skill_ids': [s1.id, s2.id, s3.id]
    }, headers=headers_admin)
    assert res_opp.status_code == 201

    # 4. Fetch opportunities as student & verify match count (2 of 3)
    res_get = client.get('/api/opportunities', headers=headers_student)
    assert res_get.status_code == 200
    opps = res_get.json['opportunities']
    assert len(opps) == 1
    assert opps[0]['matched_skills_count'] == 2
    assert opps[0]['total_skills_count'] == 3
