import pytest
from datetime import datetime, timedelta
from app.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'

from app import create_app
from app.models import (
    db, User, DeviceSession, ActivityHeartbeat, ActivitySession, Course, Enrollment,
    Competition, CompetitionParticipation, Certificate
)
from app.services.celery_tasks import rollup_activity_heartbeats, recalculate_leaderboard

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        admin = User(username='admin', email='admin@test.org', role='admin', status='approved', is_root_admin=True, is_first_login=False)
        admin.set_password('AdminPass123!')

        teacher = User(username='teacher', email='teacher@test.org', role='teacher', status='approved', is_first_login=False)
        teacher.set_password('TeacherPass123!')

        student = User(username='student', email='student@test.org', role='member', status='approved', is_first_login=False, student_id='ST-101', full_name='Alice Student')
        student.set_password('StudentPass123!')

        db.session.add_all([admin, teacher, student])
        db.session.commit()

        s_admin = DeviceSession(user_id=admin.id, session_token='token_admin', ip_address='127.0.0.1', user_agent='TestAgent', is_active=True)
        s_teacher = DeviceSession(user_id=teacher.id, session_token='token_teacher', ip_address='127.0.0.1', user_agent='TestAgent', is_active=True)
        s_student = DeviceSession(user_id=student.id, session_token='token_student', ip_address='127.0.0.1', user_agent='TestAgent', is_active=True)

        db.session.add_all([s_admin, s_teacher, s_student])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_heartbeat_and_online_status(client, app):
    headers = {'Authorization': 'Bearer token_student'}
    student = User.query.filter_by(username='student').first()

    # Send JS heartbeat ping
    res = client.post('/api/heartbeat', json={'subdomain': 'club'}, headers=headers)
    assert res.status_code == 200
    assert res.json['status'] == 'ok'

    # Check raw heartbeat recorded in DB
    hb = ActivityHeartbeat.query.filter_by(user_id=student.id).first()
    assert hb is not None
    assert hb.subdomain == 'club'

    # Check online status endpoint
    res = client.get('/api/activity/online', headers=headers)
    assert res.status_code == 200
    assert 'online_count' in res.json

def test_activity_heartbeats_celery_rollup(app, client):
    student = User.query.filter_by(username='student').first()

    # Create raw heartbeats
    now = datetime.utcnow()
    hb1 = ActivityHeartbeat(user_id=student.id, subdomain='club', ts=now)
    hb2 = ActivityHeartbeat(user_id=student.id, subdomain='club', ts=now)
    db.session.add_all([hb1, hb2])
    db.session.commit()

    # Execute rollup task passing app instance
    msg = rollup_activity_heartbeats(app)
    assert "Rolled up" in msg

    # Raw heartbeats should be pruned
    assert ActivityHeartbeat.query.count() == 0

    # ActivitySession record created
    sess = ActivitySession.query.filter_by(user_id=student.id).first()
    assert sess is not None
    assert sess.duration_seconds == 120 # 2 heartbeats * 60s

def test_teacher_student_roster_and_profile(client, app):
    teacher_headers = {'Authorization': 'Bearer token_teacher'}
    student = User.query.filter_by(username='student').first()
    now = datetime.utcnow()

    # Create dummy course & competition for student profile data
    course = Course(slug='cyber-101', title='Cyber 101', description='Introductory course', status='published')
    db.session.add(course)

    db.session.commit()

    enrollment = Enrollment(user_id=student.id, course_id=course.id, progress_percent=100.0, completed_at=now)

    comp = Competition(title='Hackathon 2026', description='Annual hackathon event', category='hackathon', priority='high', status='ended', starts_at=now, ends_at=now)
    db.session.add(comp)
    db.session.commit()

    part = CompetitionParticipation(competition_id=comp.id, user_id=student.id, result='winner', placement_label='1st Place')
    cert = Certificate(user_id=student.id, type='competition', source_id=comp.id, file_path='/uploads/certificates/cert1.pdf')

    db.session.add_all([enrollment, part, cert])
    db.session.commit()

    # 1. Roster query
    res = client.get('/api/teacher/students?q=Alice', headers=teacher_headers)
    assert res.status_code == 200
    assert len(res.json['students']) >= 1
    assert res.json['students'][0]['student_id'] == 'ST-101'

    # 2. Structured Student Profile & Trophy Case query
    res = client.get(f"/api/teacher/students/{student.id}", headers=teacher_headers)
    assert res.status_code == 200
    p = res.json
    assert p['overview']['username'] == 'student'
    assert len(p['academy']) == 1
    assert p['academy'][0]['progress_percent'] == 100.0
    assert len(p['trophy_case']) == 1
    assert p['trophy_case'][0]['result'] == 'winner'
    assert p['trophy_case'][0]['certificate']['file_path'] == '/uploads/certificates/cert1.pdf'

def test_leaderboard_rerecalculation_and_ranking(app, client):
    student = User.query.filter_by(username='student').first()
    now = datetime.utcnow()

    # Setup winner participations & completed course for student
    comp = Competition(title='CTF Derby', description='Jeopardy CTF Derby', status='ended', starts_at=now, ends_at=now)
    db.session.add(comp)
    db.session.commit()

    part = CompetitionParticipation(competition_id=comp.id, user_id=student.id, result='winner')
    db.session.add(part)
    db.session.commit()

    # Recalculate leaderboard
    msg = recalculate_leaderboard(app)
    assert "Recalculated leaderboard" in msg

    # Verify score updated (Winner = 100 points)
    updated_student = User.query.get(student.id)
    assert updated_student.leaderboard_score == 100.0

    # Fetch leaderboard endpoint
    headers = {'Authorization': 'Bearer token_student'}
    res = client.get('/api/leaderboard', headers=headers)
    assert res.status_code == 200
    assert len(res.json['leaderboard']) >= 1
    assert res.json['leaderboard'][0]['username'] == 'student'
    assert res.json['leaderboard'][0]['leaderboard_score'] == 100.0

def test_admin_analytics_endpoint(client, app):
    admin_headers = {'Authorization': 'Bearer token_admin'}

    res = client.get('/api/admin/analytics', headers=admin_headers)
    assert res.status_code == 200
    data = res.json
    assert 'registration_trend' in data
    assert 'weekly_active_members' in data
    assert 'top_courses' in data
    assert 'top_competitions' in data
    assert data['registration_trend']['total_approved'] >= 3
