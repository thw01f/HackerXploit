import os
import math
from datetime import datetime
from flask import Blueprint, request, jsonify, g, Response, send_file
from app.models import db, Course, CourseChapter, Enrollment, CourseComment, Certificate
from app.utils.decorators import require_auth, require_role, log_audit
from app.services.markdown_service import parse_markdown_frontmatter, render_sanitized_html
from app.services.pdf_service import generate_completion_certificate

academy_bp = Blueprint('academy', __name__, url_prefix='/api/academy')

@academy_bp.route('/courses', methods=['GET'])
@require_auth
def get_courses():
    if g.current_user.role in ['teacher', 'admin', 'root_admin']:
        courses = Course.query.all()
    else:
        courses = Course.query.filter_by(status='published').all()
    return jsonify({'courses': [c.to_dict() for c in courses]}), 200

@academy_bp.route('/courses', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def create_course():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Course title is required'}), 400

    slug = data.get('slug') or title.lower().replace(' ', '-')
    existing = Course.query.filter_by(slug=slug).first()
    if existing:
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

    course = Course(
        title=title,
        slug=slug,
        description=data.get('description', ''),
        cover_image=data.get('cover_image', '/uploads/courses/default_cover.png'),
        author_id=g.current_user.id,
        status=data.get('status', 'published')
    )
    db.session.add(course)
    db.session.commit()

    log_audit('COURSE_CREATE', target_type='Course', target_id=course.id, details={'title': title})
    return jsonify(course.to_dict()), 201

@academy_bp.route('/write', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def write_course_content():
    """
    Medium-style Markdown editor endpoint AND file upload (.md) endpoint.
    Parses front-matter if present and writes to content_markdown.
    """
    title = ""
    description = ""
    cover_image = ""
    markdown_text = ""
    course_id = None
    order_index = 1

    if 'file' in request.files:
        uploaded_file = request.files['file']
        raw_content = uploaded_file.read().decode('utf-8', errors='ignore')
        meta, markdown_text = parse_markdown_frontmatter(raw_content)
        title = meta.get('title', uploaded_file.filename.replace('.md', '').replace('_', ' ').title())
        description = meta.get('description', '')
        cover_image = meta.get('cover_image', '/uploads/courses/default_cover.png')
        order_index = int(meta.get('order_index', 1))
        course_id = request.form.get('course_id') or meta.get('course_id')
    else:
        data = request.get_json() or {}
        raw_content = data.get('content_markdown', '')
        meta, markdown_text = parse_markdown_frontmatter(raw_content)
        title = data.get('title') or meta.get('title', 'Untitled Chapter')
        description = data.get('description') or meta.get('description', '')
        cover_image = data.get('cover_image') or meta.get('cover_image', '/uploads/courses/default_cover.png')
        order_index = int(data.get('order_index') or meta.get('order_index', 1))
        course_id = data.get('course_id') or meta.get('course_id')

    if not markdown_text:
        return jsonify({'error': 'Markdown content is required'}), 400

    # Ensure course exists or create new one
    if course_id:
        course = Course.query.get(course_id)
    else:
        slug = title.lower().replace(' ', '-')
        existing = Course.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
        course = Course(
            title=title,
            slug=slug,
            description=description or 'Interactive Academy Course',
            cover_image=cover_image,
            author_id=g.current_user.id,
            status='published'
        )
        db.session.add(course)
        db.session.flush()

    chapter = CourseChapter(
        course_id=course.id,
        order_index=order_index,
        title=title,
        content_markdown=markdown_text,
        attachments=[]
    )
    db.session.add(chapter)
    db.session.commit()

    log_audit('CHAPTER_CREATE', target_type='CourseChapter', target_id=chapter.id, details={'course_id': course.id})
    return jsonify({'course': course.to_dict(), 'chapter': chapter.to_dict()}), 201

@academy_bp.route('/course/<slug>', methods=['GET'])
@require_auth
def get_course_by_slug(slug):
    course = Course.query.filter_by(slug=slug).first_or_404()
    enrollment = Enrollment.query.filter_by(user_id=g.current_user.id, course_id=course.id).first()

    chapters_data = []
    for ch in course.chapters:
        ch_dict = ch.to_dict()
        ch_dict['sanitized_html'] = render_sanitized_html(ch.content_markdown)
        word_count = len(ch.content_markdown.split())
        ch_dict['read_time_minutes'] = max(1, math.ceil(word_count / 200))
        chapters_data.append(ch_dict)

    data = course.to_dict()
    data['chapters'] = chapters_data
    data['enrollment'] = enrollment.to_dict() if enrollment else None
    return jsonify(data), 200

@academy_bp.route('/courses/<int:course_id>/enroll', methods=['POST'])
@require_auth
def enroll(course_id):
    course = Course.query.get_or_404(course_id)
    enrollment = Enrollment.query.filter_by(user_id=g.current_user.id, course_id=course.id).first()

    if not enrollment:
        enrollment = Enrollment(
            user_id=g.current_user.id,
            course_id=course.id,
            progress_percent=0.0,
            completed_chapters=[]
        )
        db.session.add(enrollment)
        db.session.commit()

    return jsonify(enrollment.to_dict()), 200

@academy_bp.route('/chapters/<int:chapter_id>/complete', methods=['POST'])
@require_auth
def complete_chapter(chapter_id):
    chapter = CourseChapter.query.get_or_404(chapter_id)
    course = chapter.course

    enrollment = Enrollment.query.filter_by(user_id=g.current_user.id, course_id=course.id).first()
    if not enrollment:
        enrollment = Enrollment(user_id=g.current_user.id, course_id=course.id, progress_percent=0.0, completed_chapters=[])
        db.session.add(enrollment)

    completed = set(enrollment.completed_chapters or [])
    completed.add(chapter_id)
    enrollment.completed_chapters = list(completed)

    total_chapters = len(course.chapters) or 1
    progress = (len(completed) / total_chapters) * 100.0
    enrollment.progress_percent = min(100.0, progress)

    cert_data = None
    if enrollment.progress_percent >= 100.0 and not enrollment.completed_at:
        enrollment.completed_at = datetime.utcnow()
        
        # Check if certificate already exists
        existing_cert = Certificate.query.filter_by(user_id=g.current_user.id, type='course_completion', source_id=course.id).first()
        if not existing_cert:
            cert_id = f"CERT-COURSE-{course.id}-USER-{g.current_user.id}"
            pdf_path = generate_completion_certificate(g.current_user.full_name or g.current_user.username, course.title, cert_id)
            
            cert = Certificate(
                user_id=g.current_user.id,
                type='course_completion',
                source_id=course.id,
                file_path=pdf_path
            )
            db.session.add(cert)
            cert_data = cert.to_dict()

    db.session.commit()
    
    res = enrollment.to_dict()
    if cert_data:
        res['certificate'] = cert_data
    return jsonify(res), 200

@academy_bp.route('/chapters/<int:chapter_id>/comments', methods=['GET', 'POST'])
@require_auth
def chapter_comments(chapter_id):
    chapter = CourseChapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        data = request.get_json() or {}
        body = data.get('body', '').strip()
        if not body:
            return jsonify({'error': 'Comment body is required'}), 400

        comment = CourseComment(
            course_id=chapter.course_id,
            chapter_id=chapter.id,
            user_id=g.current_user.id,
            body=body
        )
        db.session.add(comment)
        db.session.commit()
        return jsonify(comment.to_dict()), 201

    comments = CourseComment.query.filter_by(chapter_id=chapter_id).order_by(CourseComment.created_at.asc()).all()
    return jsonify({'comments': [c.to_dict() for c in comments]}), 200

@academy_bp.route('/comments/<int:comment_id>/report', methods=['POST'])
@require_auth
def report_comment(comment_id):
    comment = CourseComment.query.get_or_404(comment_id)
    comment.is_reported = True
    db.session.commit()
    log_audit('COMMENT_REPORTED', target_type='CourseComment', target_id=comment.id)
    return jsonify({'message': 'Comment reported for administrative review', 'comment': comment.to_dict()}), 200

@academy_bp.route('/my-courses', methods=['GET'])
@require_auth
def my_courses():
    enrollments = Enrollment.query.filter_by(user_id=g.current_user.id).all()
    items = []
    for enr in enrollments:
        enr_dict = enr.to_dict()
        enr_dict['course'] = enr.course.to_dict() if enr.course else None
        cert = Certificate.query.filter_by(user_id=g.current_user.id, type='course_completion', source_id=enr.course_id).first()
        enr_dict['certificate'] = cert.to_dict() if cert else None
        items.append(enr_dict)

    return jsonify({'enrollments': items}), 200

@academy_bp.route('/attachments/<int:chapter_id>/<filename>', methods=['GET'])
@require_auth
def serve_attachment(chapter_id, filename):
    """
    Gated attachment serving via Nginx X-Accel-Redirect.
    Verifies user authentication and course enrollment prior to serving file.
    """
    chapter = CourseChapter.query.get_or_404(chapter_id)
    enrollment = Enrollment.query.filter_by(user_id=g.current_user.id, course_id=chapter.course_id).first()
    
    if not enrollment and g.current_user.role not in ['teacher', 'admin', 'root_admin']:
        return jsonify({'error': 'You must be enrolled in this course to download attachments'}), 403

    # Nginx X-Accel-Redirect header setup
    internal_path = f"/internal_uploads/protected/{filename}"
    response = Response()
    response.headers['X-Accel-Redirect'] = internal_path
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
