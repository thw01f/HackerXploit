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

    import re
    raw_slug = data.get('slug') or title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', raw_slug).strip('-')
    if not slug:
        slug = f"course-{int(datetime.utcnow().timestamp())}"
    existing = Course.query.filter_by(slug=slug).first()
    if existing:
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

    course = Course(
        title=title,
        slug=slug,
        description=data.get('description', ''),
        cover_image=data.get('cover_image') or data.get('thumbnail_url') or '/uploads/courses/default_cover.png',
        difficulty=data.get('difficulty', 'Easy'),
        is_new=bool(data.get('is_new', True)),
        author_id=g.current_user.id,
        status=data.get('status', 'published')
    )
    db.session.add(course)
    db.session.commit()

    log_audit('COURSE_CREATE', target_type='Course', target_id=course.id, details={'title': title})
    return jsonify(course.to_dict()), 201

@academy_bp.route('/courses/<int:course_id>', methods=['PUT', 'DELETE'])
@require_role('teacher', 'admin', 'root_admin')
def modify_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'DELETE':
        db.session.delete(course)
        db.session.commit()
        log_audit('COURSE_DELETE', target_type='Course', target_id=course_id)
        return jsonify({'message': 'Course deleted successfully'}), 200

    data = request.get_json() or {}
    if 'title' in data:
        course.title = data['title'].strip()
    if 'description' in data:
        course.description = data['description'].strip()
    if 'cover_image' in data or 'thumbnail_url' in data:
        course.cover_image = data.get('cover_image') or data.get('thumbnail_url')
    if 'difficulty' in data:
        course.difficulty = data['difficulty']
    if 'is_new' in data:
        course.is_new = bool(data['is_new'])
    if 'status' in data:
        course.status = data['status']

    db.session.commit()
    log_audit('COURSE_UPDATE', target_type='Course', target_id=course.id)
    return jsonify(course.to_dict()), 200

@academy_bp.route('/write', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def write_course_content():
    """
    Markdown editor endpoint AND file upload (.md) endpoint.
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

    course_id_int = None
    if course_id:
        try:
            course_id_int = int(course_id)
        except (ValueError, TypeError):
            course_id_int = None

    course = Course.query.get(course_id_int) if course_id_int else None

    try:
        # Ensure course exists or create new one
        if not course:
            import re
            slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
            if not slug:
                slug = f"note-{int(datetime.utcnow().timestamp())}"
            existing = Course.query.filter_by(slug=slug).first()
            if existing:
                slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
            course = Course(
                title=title,
                slug=slug,
                description=description or 'Interactive Academy Module Note',
                cover_image=cover_image or '/uploads/courses/default_cover.png',
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
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@academy_bp.route('/courses/<int:course_id>/reorder-chapters', methods=['PUT'])
@require_role('teacher', 'admin', 'root_admin')
def reorder_course_chapters(course_id):
    """
    Reorders chapters for a given course.
    Expects payload: { "chapter_ids": [3, 1, 2] }
    """
    course = Course.query.get_or_404(course_id)
    data = request.get_json() or {}
    chapter_ids = data.get('chapter_ids', [])

    if not isinstance(chapter_ids, list):
        return jsonify({'error': 'chapter_ids must be a list'}), 400

    for index, ch_id in enumerate(chapter_ids, start=1):
        chapter = CourseChapter.query.filter_by(id=ch_id, course_id=course.id).first()
        if chapter:
            chapter.order_index = index

    db.session.commit()
    log_audit('CHAPTERS_REORDERED', target_type='Course', target_id=course.id)
    return jsonify({'message': 'Chapters reordered successfully'}), 200

@academy_bp.route('/chapters/<int:chapter_id>', methods=['PUT', 'DELETE'])
@require_role('teacher', 'admin', 'root_admin')
def modify_chapter(chapter_id):
    chapter = CourseChapter.query.get_or_404(chapter_id)

    if request.method == 'DELETE':
        db.session.delete(chapter)
        db.session.commit()
        log_audit('CHAPTER_DELETED', target_type='CourseChapter', target_id=chapter_id)
        return jsonify({'message': 'Chapter deleted successfully'}), 200

    data = request.get_json() or {}
    if 'title' in data:
        chapter.title = data['title'].strip()
    if 'content_markdown' in data:
        chapter.content_markdown = data['content_markdown']
    if 'order_index' in data:
        chapter.order_index = int(data['order_index'])

    db.session.commit()
    log_audit('CHAPTER_UPDATED', target_type='CourseChapter', target_id=chapter.id)
    return jsonify(chapter.to_dict()), 200

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

@academy_bp.route('/courses/<int:course_id>/chapters/<int:chapter_id>/attachments', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def upload_chapter_attachment(course_id, chapter_id):
    """
    Stores course attachments (PDFs, images, zip labs) under /data/academy/<course_id>/
    and attaches filename to chapter metadata.
    """
    from werkzeug.utils import secure_filename
    from flask import current_app

    chapter = CourseChapter.query.filter_by(id=chapter_id, course_id=course_id).first_or_404()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file or not file.filename:
        return jsonify({'error': 'Empty filename'}), 400

    filename = secure_filename(file.filename)
    dest_dir = os.path.join('/data/academy', str(course_id))
    try:
        os.makedirs(dest_dir, exist_ok=True)
    except Exception:
        dest_dir = os.path.join(current_app.root_path, '..', 'data', 'academy', str(course_id))
        os.makedirs(dest_dir, exist_ok=True)

    file_path = os.path.join(dest_dir, filename)
    file.save(file_path)

    existing_atts = list(chapter.attachments or [])
    if not any(a.get('name') == filename for a in existing_atts):
        existing_atts.append({
            'name': filename,
            'url': f"/api/academy/attachments/{chapter.id}/{filename}",
            'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
        })
        chapter.attachments = existing_atts
        db.session.commit()

    return jsonify({'message': 'Attachment uploaded successfully', 'attachments': chapter.attachments}), 201

@academy_bp.route('/attachments/<int:chapter_id>/<filename>', methods=['GET'])
@require_auth
def serve_attachment(chapter_id, filename):
    """
    Gated attachment serving via Nginx X-Accel-Redirect (with send_file fallback).
    Verifies user authentication and course enrollment prior to serving file.
    """
    from werkzeug.utils import secure_filename
    from flask import current_app

    chapter = CourseChapter.query.get_or_404(chapter_id)
    enrollment = Enrollment.query.filter_by(user_id=g.current_user.id, course_id=chapter.course_id).first()
    
    if not enrollment and g.current_user.role not in ['teacher', 'admin', 'root_admin']:
        return jsonify({'error': 'You must be enrolled in this course to download attachments'}), 403

    safe_name = secure_filename(filename)
    primary_path = os.path.join('/data/academy', str(chapter.course_id), safe_name)
    fallback_path = os.path.join(current_app.root_path, '..', 'data', 'academy', str(chapter.course_id), safe_name)

    target_path = primary_path if os.path.exists(primary_path) else fallback_path

    if not os.path.exists(target_path):
        return jsonify({'error': 'Attachment file not found'}), 404

    # Nginx X-Accel-Redirect header setup
    if request.headers.get('X-Nginx-Proxy'):
        internal_path = f"/internal_academy/{chapter.course_id}/{safe_name}"
        response = Response()
        response.headers['X-Accel-Redirect'] = internal_path
        response.headers['Content-Type'] = 'application/octet-stream'
        response.headers['Content-Disposition'] = f'attachment; filename="{safe_name}"'
        return response

    return send_file(target_path, as_attachment=True, download_name=safe_name)

# -------------------------------------------------------------------
# Live Classes Platform (TryHackMe-style live sessions)
# -------------------------------------------------------------------
@academy_bp.route('/live-classes', methods=['GET'])
@require_auth
def get_live_classes():
    from app.models.academy import LiveClass
    classes = LiveClass.query.order_by(LiveClass.scheduled_at.asc()).all()
    return jsonify({'live_classes': [c.to_dict() for c in classes]}), 200

@academy_bp.route('/live-classes', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def create_live_class():
    from app.models.academy import LiveClass
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    meeting_link = data.get('meeting_link', '').strip()
    
    if not title or not meeting_link:
        return jsonify({'error': 'Title and meeting link are required'}), 400

    scheduled_at_str = data.get('scheduled_at')
    try:
        scheduled_at = datetime.fromisoformat(scheduled_at_str.replace('Z', '+00:00')) if scheduled_at_str else datetime.utcnow()
    except Exception:
        scheduled_at = datetime.utcnow()

    live_item = LiveClass(
        title=title,
        description=data.get('description', ''),
        meeting_link=meeting_link,
        thumbnail_url=data.get('thumbnail_url') or data.get('cover_image') or '/uploads/courses/default_cover.png',
        scheduled_at=scheduled_at,
        duration_minutes=int(data.get('duration_minutes', 60)),
        instructor_id=g.current_user.id
    )
    db.session.add(live_item)
    db.session.commit()

    log_audit('LIVE_CLASS_CREATED', target_type='LiveClass', target_id=live_item.id, details={'title': title})
    return jsonify(live_item.to_dict()), 201

@academy_bp.route('/live-classes/<int:live_id>', methods=['PUT', 'DELETE'])
@require_role('teacher', 'admin', 'root_admin')
def delete_live_class(live_id):
    from app.models.academy import LiveClass
    live_item = LiveClass.query.get_or_404(live_id)

    if request.method == 'DELETE':
        db.session.delete(live_item)
        db.session.commit()
        log_audit('LIVE_CLASS_DELETED', target_type='LiveClass', target_id=live_id)
        return jsonify({'message': 'Live class session cancelled'}), 200

    data = request.get_json() or {}
    if 'title' in data:
        live_item.title = data['title'].strip()
    if 'description' in data:
        live_item.description = data['description'].strip()
    if 'meeting_link' in data:
        live_item.meeting_link = data['meeting_link'].strip()
    if 'thumbnail_url' in data or 'cover_image' in data:
        live_item.thumbnail_url = data.get('thumbnail_url') or data.get('cover_image')
    if 'duration_minutes' in data:
        live_item.duration_minutes = int(data['duration_minutes'])
    if 'scheduled_at' in data:
        try:
            live_item.scheduled_at = datetime.fromisoformat(data['scheduled_at'].replace('Z', '+00:00'))
        except Exception:
            pass

    db.session.commit()
    log_audit('LIVE_CLASS_UPDATED', target_type='LiveClass', target_id=live_item.id)
    return jsonify(live_item.to_dict()), 200
