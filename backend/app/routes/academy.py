from datetime import datetime
from flask import Blueprint, request, jsonify, g
from app.models import db, Course, Module, Lesson, CourseEnrollment
from app.utils.decorators import require_auth, require_role, log_audit

academy_bp = Blueprint('academy', __name__, url_prefix='/api/academy')

@academy_bp.route('/courses', methods=['GET'])
@require_auth
def get_courses():
    if g.current_user.role in ['teacher', 'admin', 'root_admin']:
        courses = Course.query.all()
    else:
        courses = Course.query.filter_by(is_published=True).all()
    return jsonify({'courses': [c.to_dict() for c in courses]}), 200

@academy_bp.route('/courses', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def create_course():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    slug = title.lower().replace(' ', '-')
    description = data.get('description', '')

    if not title or not description:
        return jsonify({'error': 'Title and description are required'}), 400

    course = Course(
        title=title,
        slug=slug,
        description=description,
        category=data.get('category', 'General'),
        difficulty=data.get('difficulty', 'Beginner'),
        thumbnail_url=data.get('thumbnail_url'),
        author_id=g.current_user.id,
        is_published=data.get('is_published', False)
    )
    db.session.add(course)
    db.session.commit()

    log_audit('COURSE_CREATE', target_type='Course', target_id=course.id, details={'title': title})
    return jsonify(course.to_dict()), 201

@academy_bp.route('/courses/<int:course_id>', methods=['GET'])
@require_auth
def get_course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    enrollment = CourseEnrollment.query.filter_by(user_id=g.current_user.id, course_id=course_id).first()
    
    data = course.to_dict()
    data['modules'] = [m.to_dict() for m in course.modules]
    data['enrollment'] = enrollment.to_dict() if enrollment else None
    return jsonify(data), 200

@academy_bp.route('/courses/<int:course_id>/enroll', methods=['POST'])
@require_auth
def enroll_course(course_id):
    course = Course.query.get_or_404(course_id)
    enrollment = CourseEnrollment.query.filter_by(user_id=g.current_user.id, course_id=course_id).first()
    if not enrollment:
        enrollment = CourseEnrollment(
            user_id=g.current_user.id,
            course_id=course_id,
            completed_lessons=[]
        )
        db.session.add(enrollment)
        db.session.commit()
    return jsonify(enrollment.to_dict()), 200

@academy_bp.route('/courses/<int:course_id>/modules', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def add_module(course_id):
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Module title required'}), 400

    mod = Module(
        course_id=course_id,
        title=title,
        order=data.get('order', 1)
    )
    db.session.add(mod)
    db.session.commit()
    return jsonify(mod.to_dict()), 201

@academy_bp.route('/modules/<int:module_id>/lessons', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def add_lesson(module_id):
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    content = data.get('content_markdown', '')
    if not title or not content:
        return jsonify({'error': 'Lesson title and content required'}), 400

    lesson = Lesson(
        module_id=module_id,
        title=title,
        content_markdown=content,
        video_url=data.get('video_url'),
        attachment_url=data.get('attachment_url'),
        order=data.get('order', 1)
    )
    db.session.add(lesson)
    db.session.commit()
    return jsonify(lesson.to_dict()), 201

@academy_bp.route('/lessons/<int:lesson_id>/complete', methods=['POST'])
@require_auth
def complete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course_id = lesson.module.course_id
    enrollment = CourseEnrollment.query.filter_by(user_id=g.current_user.id, course_id=course_id).first()
    if not enrollment:
        enrollment = CourseEnrollment(user_id=g.current_user.id, course_id=course_id, completed_lessons=[])
        db.session.add(enrollment)

    completed = set(enrollment.completed_lessons or [])
    completed.add(lesson_id)
    enrollment.completed_lessons = list(completed)

    # Check if all lessons in course are finished
    all_lessons = Lesson.query.join(Module).filter(Module.course_id == course_id).all()
    if all_lessons and len(completed) >= len(all_lessons):
        enrollment.is_completed = True
        enrollment.completed_at = datetime.utcnow()
        enrollment.certificate_url = f"/uploads/certificates/cert_course_{course_id}_user_{g.current_user.id}.pdf"

    db.session.commit()
    return jsonify(enrollment.to_dict()), 200
