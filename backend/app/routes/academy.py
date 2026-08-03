import os
import math
from datetime import datetime
from flask import Blueprint, request, jsonify, g, Response, send_file
from app.models import db, Course, CourseChapter, ModuleNote, Enrollment, CourseComment, Certificate, CourseResource, NoteRating
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

    enrollments_by_course = {e.course_id: e for e in Enrollment.query.filter_by(user_id=g.current_user.id).all()}

    results = []
    for c in courses:
        c_dict = c.to_dict()
        e = enrollments_by_course.get(c.id)
        c_dict['enrollment'] = {
            'progress_percent': e.progress_percent,
            'is_completed': bool(e.completed_at) or e.progress_percent >= 100.0
        } if e else None
        results.append(c_dict)

    return jsonify({'courses': results}), 200

def _module_read_minutes(module):
    total = 0
    for note in module.notes:
        total += max(1, math.ceil(len(note.content_markdown.split()) / 200))
    return total

@academy_bp.route('/modules', methods=['GET'])
@require_auth
def get_all_modules():
    """Flat list of every Module across every Path, for the Academy
    'Modules' tab - browsing by individual module rather than by path."""
    is_staff = g.current_user.role in ['teacher', 'admin', 'root_admin']
    courses = Course.query.all() if is_staff else Course.query.filter_by(status='published').all()

    modules = []
    for course in courses:
        for ch in course.chapters:
            modules.append({
                'id': ch.id,
                'title': ch.title,
                'description': ch.description or '',
                'cover_image': ch.cover_image or '/default-cover.svg',
                'order_index': ch.order_index,
                'notes_count': len(ch.notes),
                'read_time_minutes': _module_read_minutes(ch),
                'course_id': course.id,
                'course_slug': course.slug,
                'course_title': course.title,
                'difficulty': course.difficulty,
                'status': course.status
            })

    modules.sort(key=lambda m: (m['course_title'], m['order_index']))
    return jsonify({'modules': modules}), 200

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
        cover_image=data.get('cover_image') or data.get('thumbnail_url') or '/default-cover.svg',
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

@academy_bp.route('/courses/<int:course_id>/resources', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def create_course_resource(course_id):
    course = Course.query.get_or_404(course_id)
    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    resource_type = data.get('resource_type') or 'link'

    if not title:
        return jsonify({'error': 'Title is required'}), 400
    if resource_type != 'note' and not (data.get('url') or '').strip():
        return jsonify({'error': 'URL is required for this resource type'}), 400

    resource = CourseResource(
        course_id=course.id,
        title=title,
        url=(data.get('url') or '').strip(),
        resource_type=resource_type,
        description=(data.get('description') or '').strip(),
        order_index=len(course.resources) + 1
    )
    db.session.add(resource)
    db.session.commit()

    log_audit('COURSE_RESOURCE_CREATE', target_type='CourseResource', target_id=resource.id, notes=f"Resource '{title}' added to course '{course.slug}'")
    return jsonify(resource.to_dict()), 201

@academy_bp.route('/courses/resources/<int:resource_id>', methods=['PUT', 'DELETE'])
@require_role('teacher', 'admin', 'root_admin')
def modify_course_resource(resource_id):
    resource = CourseResource.query.get_or_404(resource_id)

    if request.method == 'DELETE':
        db.session.delete(resource)
        db.session.commit()
        log_audit('COURSE_RESOURCE_DELETE', target_type='CourseResource', target_id=resource_id)
        return jsonify({'message': 'Resource deleted successfully'}), 200

    data = request.get_json() or {}
    if 'title' in data:
        resource.title = data['title'].strip()
    if 'url' in data:
        resource.url = data['url'].strip()
    if 'resource_type' in data:
        resource.resource_type = data['resource_type']
    if 'description' in data:
        resource.description = data['description'].strip()
    if 'order_index' in data:
        resource.order_index = data['order_index']

    db.session.commit()
    log_audit('COURSE_RESOURCE_UPDATE', target_type='CourseResource', target_id=resource_id)
    return jsonify(resource.to_dict()), 200

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
        cover_image = meta.get('cover_image', '/default-cover.svg')
        order_index = int(meta.get('order_index', 1))
        course_id = request.form.get('course_id') or meta.get('course_id')
    else:
        data = request.get_json() or {}
        raw_content = data.get('content_markdown', '')
        meta, markdown_text = parse_markdown_frontmatter(raw_content)
        title = data.get('title') or meta.get('title', 'Untitled Chapter')
        description = data.get('description') or meta.get('description', '')
        cover_image = data.get('cover_image') or meta.get('cover_image', '/default-cover.svg')
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
                cover_image=cover_image or '/default-cover.svg',
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
    Reorders Modules within a given Path.
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
    log_audit('MODULES_REORDERED', target_type='Course', target_id=course.id)
    return jsonify({'message': 'Modules reordered successfully'}), 200

@academy_bp.route('/courses/<int:course_id>/modules', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def create_module(course_id):
    course = Course.query.get_or_404(course_id)
    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'error': 'Module title is required'}), 400

    module = CourseChapter(
        course_id=course.id,
        order_index=len(course.chapters) + 1,
        title=title,
        description=(data.get('description') or '').strip(),
        cover_image=data.get('cover_image') or None,
        content_markdown=''  # legacy column, unused - see model comment
    )
    db.session.add(module)
    db.session.commit()

    log_audit('MODULE_CREATE', target_type='CourseChapter', target_id=module.id, details={'course_id': course.id, 'title': title})
    return jsonify(module.to_dict()), 201

@academy_bp.route('/chapters/<int:chapter_id>', methods=['PUT', 'DELETE'])
@require_role('teacher', 'admin', 'root_admin')
def modify_chapter(chapter_id):
    module = CourseChapter.query.get_or_404(chapter_id)

    if request.method == 'DELETE':
        db.session.delete(module)
        db.session.commit()
        log_audit('MODULE_DELETED', target_type='CourseChapter', target_id=chapter_id)
        return jsonify({'message': 'Module deleted successfully'}), 200

    data = request.get_json() or {}
    if 'title' in data:
        module.title = data['title'].strip()
    if 'description' in data:
        module.description = data['description'].strip()
    if 'cover_image' in data:
        module.cover_image = data['cover_image']
    if 'order_index' in data:
        module.order_index = int(data['order_index'])

    db.session.commit()
    log_audit('MODULE_UPDATED', target_type='CourseChapter', target_id=module.id)
    return jsonify(module.to_dict()), 200

@academy_bp.route('/modules/<int:module_id>/notes', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def create_note(module_id):
    module = CourseChapter.query.get_or_404(module_id)
    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    content_markdown = data.get('content_markdown', '')
    if not title:
        return jsonify({'error': 'Note title is required'}), 400

    note = ModuleNote(
        chapter_id=module.id,
        order_index=len(module.notes) + 1,
        title=title,
        content_markdown=content_markdown,
        attachments=[]
    )
    db.session.add(note)
    db.session.commit()

    log_audit('NOTE_CREATE', target_type='ModuleNote', target_id=note.id, details={'module_id': module.id, 'title': title})
    return jsonify(note.to_dict()), 201

@academy_bp.route('/notes/<int:note_id>', methods=['GET'])
@require_role('teacher', 'admin', 'root_admin')
def get_note(note_id):
    """Single note with content, for the note editor's edit mode."""
    note = ModuleNote.query.get_or_404(note_id)
    data = note.to_dict()
    data['module'] = {'id': note.module.id, 'title': note.module.title, 'course_id': note.module.course_id, 'course_slug': note.module.course.slug}
    return jsonify(data), 200

@academy_bp.route('/notes/<int:note_id>', methods=['PUT', 'DELETE'])
@require_role('teacher', 'admin', 'root_admin')
def modify_note(note_id):
    note = ModuleNote.query.get_or_404(note_id)

    if request.method == 'DELETE':
        db.session.delete(note)
        db.session.commit()
        log_audit('NOTE_DELETED', target_type='ModuleNote', target_id=note_id)
        return jsonify({'message': 'Note deleted successfully'}), 200

    data = request.get_json() or {}
    if 'title' in data:
        note.title = data['title'].strip()
    if 'content_markdown' in data:
        note.content_markdown = data['content_markdown']
    if 'order_index' in data:
        note.order_index = int(data['order_index'])

    db.session.commit()
    log_audit('NOTE_UPDATED', target_type='ModuleNote', target_id=note.id)
    return jsonify(note.to_dict()), 200

@academy_bp.route('/modules/<int:module_id>/reorder-notes', methods=['PUT'])
@require_role('teacher', 'admin', 'root_admin')
def reorder_notes(module_id):
    """Expects payload: { "note_ids": [3, 1, 2] }"""
    module = CourseChapter.query.get_or_404(module_id)
    data = request.get_json() or {}
    note_ids = data.get('note_ids', [])

    if not isinstance(note_ids, list):
        return jsonify({'error': 'note_ids must be a list'}), 400

    for index, note_id in enumerate(note_ids, start=1):
        note = ModuleNote.query.filter_by(id=note_id, chapter_id=module.id).first()
        if note:
            note.order_index = index

    db.session.commit()
    log_audit('NOTES_REORDERED', target_type='CourseChapter', target_id=module.id)
    return jsonify({'message': 'Notes reordered successfully'}), 200

@academy_bp.route('/modules/<int:module_id>/overview', methods=['GET'])
@require_auth
def get_module_overview(module_id):
    """Module cover page: module info + a Notes outline (titles + read time,
    no content) + parent Path context for the breadcrumb + course-level
    enrollment/progress. Mirrors get_course_overview one level down."""
    module = CourseChapter.query.get_or_404(module_id)
    course = module.course
    enrollment = Enrollment.query.filter_by(user_id=g.current_user.id, course_id=course.id).first()
    completed_note_ids = set(enrollment.completed_chapters or []) if enrollment else set()

    notes_outline = []
    notes_completed = 0
    for note in module.notes:
        read_time = max(1, math.ceil(len(note.content_markdown.split()) / 200))
        is_completed = note.id in completed_note_ids
        if is_completed:
            notes_completed += 1
        notes_outline.append({
            'id': note.id,
            'order_index': note.order_index,
            'title': note.title,
            'read_time_minutes': read_time,
            'has_attachments': bool(note.attachments),
            'is_completed': is_completed
        })

    data = module.to_dict()
    data['notes'] = notes_outline
    data['total_read_minutes'] = sum(n['read_time_minutes'] for n in notes_outline)
    data['course'] = {'id': course.id, 'slug': course.slug, 'title': course.title}
    data['enrollment'] = enrollment.to_dict() if enrollment else None
    # Distinct from enrollment.progress_percent (which is Path-wide, across
    # every Module in the course) - this is scoped to just this Module, so a
    # student who finished this Module's notes but not the rest of the Path
    # can see that clearly instead of reading the Path percentage as "stuck".
    data['module_notes_completed'] = notes_completed
    data['module_notes_total'] = len(notes_outline)
    data['module_progress_percent'] = round((notes_completed / len(notes_outline)) * 100.0, 1) if notes_outline else 0
    return jsonify(data), 200

@academy_bp.route('/modules/<int:module_id>/read', methods=['GET'])
@require_auth
def get_module_read(module_id):
    """Full reader payload for a Module: every Note WITH rendered content."""
    module = CourseChapter.query.get_or_404(module_id)
    course = module.course
    enrollment = Enrollment.query.filter_by(user_id=g.current_user.id, course_id=course.id).first()

    notes_data = []
    for note in module.notes:
        note_dict = note.to_dict()
        note_dict['sanitized_html'] = render_sanitized_html(note.content_markdown)
        note_dict['read_time_minutes'] = max(1, math.ceil(len(note.content_markdown.split()) / 200))
        notes_data.append(note_dict)

    data = module.to_dict()
    data['notes'] = notes_data
    data['course'] = {'id': course.id, 'slug': course.slug, 'title': course.title}
    data['enrollment'] = enrollment.to_dict() if enrollment else None
    return jsonify(data), 200

@academy_bp.route('/course/<slug>/overview', methods=['GET'])
@require_auth
def get_course_overview(slug):
    """Path cover page: a Modules outline (title/description/cover_image/
    notes_count, no note content), resources (videos/links/notes), and
    enrollment status."""
    course = Course.query.filter_by(slug=slug).first_or_404()
    enrollment = Enrollment.query.filter_by(user_id=g.current_user.id, course_id=course.id).first()
    completed_note_ids = set(enrollment.completed_chapters or []) if enrollment else set()

    modules_outline = []
    total_read_minutes = 0
    for ch in course.chapters:
        read_time = _module_read_minutes(ch)
        total_read_minutes += read_time
        module_dict = ch.to_dict()
        module_dict['read_time_minutes'] = read_time

        notes_total = len(ch.notes)
        notes_completed = sum(1 for n in ch.notes if n.id in completed_note_ids)
        module_dict['notes_completed'] = notes_completed
        module_dict['is_completed'] = notes_total > 0 and notes_completed == notes_total
        module_dict['is_in_progress'] = 0 < notes_completed < notes_total
        modules_outline.append(module_dict)

    data = course.to_dict()
    data['modules'] = modules_outline
    data['resources'] = [r.to_dict() for r in course.resources]
    data['enrollment'] = enrollment.to_dict() if enrollment else None
    data['total_read_minutes'] = total_read_minutes
    return jsonify(data), 200

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
    data['resources'] = [r.to_dict() for r in course.resources]
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

@academy_bp.route('/notes/<int:note_id>/complete', methods=['POST'])
@require_auth
def complete_note(note_id):
    """Progress is now tracked per-Note (the actual readable leaf content)
    rather than per-Module - completed_chapters keeps its original column
    name for backward compat but stores Note ids now that Modules are a
    container rather than the trackable unit."""
    note = ModuleNote.query.get_or_404(note_id)
    course = note.module.course

    enrollment = Enrollment.query.filter_by(user_id=g.current_user.id, course_id=course.id).first()
    if not enrollment:
        enrollment = Enrollment(user_id=g.current_user.id, course_id=course.id, progress_percent=0.0, completed_chapters=[])
        db.session.add(enrollment)

    completed = set(enrollment.completed_chapters or [])
    completed.add(note_id)
    enrollment.completed_chapters = list(completed)

    total_notes = sum(len(ch.notes) for ch in course.chapters) or 1
    progress = (len(completed) / total_notes) * 100.0
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

@academy_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@require_role('teacher', 'admin', 'root_admin')
def delete_comment(comment_id):
    comment = CourseComment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    log_audit('COMMENT_DELETE', target_type='CourseComment', target_id=comment_id, details={'chapter_id': comment.chapter_id})
    return jsonify({'message': 'Comment deleted successfully'}), 200

@academy_bp.route('/notes/<int:note_id>/rating', methods=['GET'])
@require_auth
def get_note_rating(note_id):
    ModuleNote.query.get_or_404(note_id)
    ratings = NoteRating.query.filter_by(note_id=note_id).all()
    my_rating = next((r.rating for r in ratings if r.user_id == g.current_user.id), None)
    return jsonify({
        'average_rating': round(sum(r.rating for r in ratings) / len(ratings), 1) if ratings else 0,
        'total_ratings': len(ratings),
        'my_rating': my_rating
    }), 200

@academy_bp.route('/notes/<int:note_id>/rating', methods=['POST'])
@require_auth
def rate_note(note_id):
    ModuleNote.query.get_or_404(note_id)
    data = request.get_json() or {}
    rating_value = data.get('rating')
    if not isinstance(rating_value, int) or rating_value < 1 or rating_value > 5:
        return jsonify({'error': 'Rating must be an integer from 1 to 5'}), 400

    existing = NoteRating.query.filter_by(note_id=note_id, user_id=g.current_user.id).first()
    if existing:
        existing.rating = rating_value
        existing.updated_at = datetime.utcnow()
    else:
        db.session.add(NoteRating(note_id=note_id, user_id=g.current_user.id, rating=rating_value))
    db.session.commit()

    ratings = NoteRating.query.filter_by(note_id=note_id).all()
    return jsonify({
        'average_rating': round(sum(r.rating for r in ratings) / len(ratings), 1) if ratings else 0,
        'total_ratings': len(ratings),
        'my_rating': rating_value
    }), 200

@academy_bp.route('/notes/<int:note_id>/reviews', methods=['GET', 'POST'])
@require_auth
def note_reviews(note_id):
    """One review (a CourseComment with note_id set) per user per note,
    paired with the star rating above - posting again edits your existing
    review rather than creating a second one."""
    note = ModuleNote.query.get_or_404(note_id)

    if request.method == 'POST':
        data = request.get_json() or {}
        body = (data.get('body') or '').strip()
        if not body:
            return jsonify({'error': 'Review text is required'}), 400

        existing = CourseComment.query.filter_by(note_id=note_id, user_id=g.current_user.id).first()
        if existing:
            existing.body = body
            existing.created_at = datetime.utcnow()
        else:
            existing = CourseComment(
                course_id=note.module.course_id,
                chapter_id=note.chapter_id,
                note_id=note_id,
                user_id=g.current_user.id,
                body=body
            )
            db.session.add(existing)
        db.session.commit()
        return jsonify(existing.to_dict()), 201

    reviews = CourseComment.query.filter_by(note_id=note_id).order_by(CourseComment.created_at.asc()).all()
    return jsonify({'comments': [r.to_dict() for r in reviews]}), 200

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

@academy_bp.route('/courses/<int:course_id>/notes/<int:note_id>/attachments', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def upload_note_attachment(course_id, note_id):
    """
    Stores course attachments (PDFs, images, zip labs) under /data/academy/<course_id>/
    and attaches filename to Note metadata (attachments now live on the Note,
    the actual readable unit, rather than the Module container).
    """
    from werkzeug.utils import secure_filename
    from flask import current_app

    note = ModuleNote.query.get_or_404(note_id)
    if note.module.course_id != course_id:
        return jsonify({'error': 'Note does not belong to this course'}), 404

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

    existing_atts = list(note.attachments or [])
    if not any(a.get('name') == filename for a in existing_atts):
        existing_atts.append({
            'name': filename,
            'url': f"/api/academy/attachments/{note.id}/{filename}",
            'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
        })
        note.attachments = existing_atts
        db.session.commit()

    return jsonify({'message': 'Attachment uploaded successfully', 'attachments': note.attachments}), 201

@academy_bp.route('/attachments/<int:note_id>/<filename>', methods=['GET'])
@require_auth
def serve_attachment(note_id, filename):
    """
    Gated attachment serving via Nginx X-Accel-Redirect (with send_file fallback).
    Verifies user authentication and course enrollment prior to serving file.
    """
    from werkzeug.utils import secure_filename
    from flask import current_app

    note = ModuleNote.query.get_or_404(note_id)
    course_id = note.module.course_id
    enrollment = Enrollment.query.filter_by(user_id=g.current_user.id, course_id=course_id).first()

    if not enrollment and g.current_user.role not in ['teacher', 'admin', 'root_admin']:
        return jsonify({'error': 'You must be enrolled in this course to download attachments'}), 403

    safe_name = secure_filename(filename)
    primary_path = os.path.join('/data/academy', str(course_id), safe_name)
    fallback_path = os.path.join(current_app.root_path, '..', 'data', 'academy', str(course_id), safe_name)

    target_path = primary_path if os.path.exists(primary_path) else fallback_path

    if not os.path.exists(target_path):
        return jsonify({'error': 'Attachment file not found'}), 404

    # Nginx X-Accel-Redirect header setup
    if request.headers.get('X-Nginx-Proxy'):
        internal_path = f"/internal_academy/{course_id}/{safe_name}"
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
    import re
    from app.models.academy import LiveClass
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    meeting_link = data.get('meeting_link', '').strip()
    # A link pasted without a scheme (e.g. "meet.google.com/xyz") gets
    # rendered as an <a href="..."> on the frontend - without this, the
    # browser treats it as a path relative to the current page instead of
    # an external URL, silently routing "Join Live Class" into the SPA.
    if meeting_link and not re.match(r'^https?://', meeting_link, re.IGNORECASE):
        meeting_link = f'https://{meeting_link}'

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
        thumbnail_url=data.get('thumbnail_url') or data.get('cover_image') or '/default-cover.svg',
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
        import re
        link = data['meeting_link'].strip()
        if link and not re.match(r'^https?://', link, re.IGNORECASE):
            link = f'https://{link}'
        live_item.meeting_link = link
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
