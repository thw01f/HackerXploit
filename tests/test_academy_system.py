import os
import pytest
from app.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'

from app import create_app
from app.models import db, User, DeviceSession, Course, CourseChapter, Enrollment, CourseComment, Certificate
from app.services.markdown_service import parse_markdown_frontmatter, render_sanitized_html
from app.services.pdf_service import generate_completion_certificate

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_teacher_token(app):
    with app.app_context():
        user = User(
            username='teacher1',
            email='teacher1@hackerxploit.org',
            password_hash='dummy_hash',
            role='teacher',
            status='approved',
            is_first_login=False
        )
        db.session.add(user)
        db.session.commit()

        sess = DeviceSession(user_id=user.id, session_token='token_teacher_123', ip_address='127.0.0.1', user_agent='TestAgent', is_active=True)
        db.session.add(sess)
        db.session.commit()
        return 'token_teacher_123'

@pytest.fixture
def auth_student_token(app):
    with app.app_context():
        user = User(
            username='student1',
            email='student1@hackerxploit.org',
            password_hash='dummy_hash',
            role='member',
            status='approved',
            is_first_login=False
        )
        db.session.add(user)
        db.session.commit()

        sess = DeviceSession(user_id=user.id, session_token='token_student_456', ip_address='127.0.0.1', user_agent='TestAgent', is_active=True)
        db.session.add(sess)
        db.session.commit()
        return 'token_student_456'

def test_markdown_frontmatter_parser():
    content = """---
title: "Advanced Exploitation"
description: "Kernel vulnerability analysis"
cover_image: "/uploads/cover.png"
order_index: 2
---

# Chapter Content
This is markdown content.
"""
    meta, body = parse_markdown_frontmatter(content)
    assert meta['title'] == "Advanced Exploitation"
    assert meta['description'] == "Kernel vulnerability analysis"
    assert meta['cover_image'] == "/uploads/cover.png"
    assert meta['order_index'] == "2"
    assert body.startswith("# Chapter Content")

def test_xss_html_sanitizer():
    raw_md = "# Header\n\n<script>alert('XSS')</script>\n<img src='x' onload='alert(1)' />"
    sanitized = render_sanitized_html(raw_md)
    assert "<script>" not in sanitized
    assert "onload=" not in sanitized
    assert "<h1>Header</h1>" in sanitized

def test_pdf_certificate_generator(tmp_path):
    cert_dir = str(tmp_path / "certificates")
    path = generate_completion_certificate("Alice Smith", "Reverse Engineering 101", "CERT-12345", output_dir=cert_dir)
    assert path.startswith("/uploads/certificates/certificate_CERT-12345.pdf")
    assert os.path.exists(os.path.join(cert_dir, "certificate_CERT-12345.pdf"))

def test_academy_flow_and_auto_certificate(client, auth_teacher_token, auth_student_token):
    # 1. Login teacher and create course chapter
    res = client.post('/api/academy/write', json={
        'title': 'Binary Exploitation 101',
        'description': 'Buffer overflow fundamentals',
        'order_index': 1,
        'content_markdown': '# Lesson 1\nIntroduction to stack frames.'
    }, headers={'Authorization': f'Bearer {auth_teacher_token}'})
    assert res.status_code == 201
    course_id = res.json['course']['id']
    chapter_id = res.json['chapter']['id']

    # 2. Switch to student and view course details
    res = client.get(f"/api/academy/course/binary-exploitation-101", headers={'Authorization': f'Bearer {auth_student_token}'})
    assert res.status_code == 200
    assert res.json['title'] == 'Binary Exploitation 101'

    # 3. Complete chapter -> reach 100% progress and auto-generate certificate
    res = client.post(f"/api/academy/chapters/{chapter_id}/complete", headers={'Authorization': f'Bearer {auth_student_token}'})
    assert res.status_code == 200
    assert res.json['progress_percent'] == 100.0
    assert 'certificate' in res.json
    assert res.json['certificate']['type'] == 'course_completion'

    # 4. Check /api/academy/my-courses
    res = client.get('/api/academy/my-courses', headers={'Authorization': f'Bearer {auth_student_token}'})
    assert res.status_code == 200
    assert len(res.json['enrollments']) == 1
    assert res.json['enrollments'][0]['certificate']['file_path'].startswith('/uploads/certificates/')

    # 5. Comment and Report Comment
    res = client.post(f"/api/academy/chapters/{chapter_id}/comments", json={'body': 'Great chapter!'}, headers={'Authorization': f'Bearer {auth_student_token}'})
    assert res.status_code == 201
    comment_id = res.json['id']

    res = client.post(f"/api/academy/comments/{comment_id}/report", headers={'Authorization': f'Bearer {auth_student_token}'})
    assert res.status_code == 200
    assert res.json['comment']['is_reported'] is True

def test_site_search(client, auth_student_token):
    res = client.get('/api/search?q=Binary', headers={'Authorization': f'Bearer {auth_student_token}'})
    assert res.status_code == 200
    assert 'results' in res.json
