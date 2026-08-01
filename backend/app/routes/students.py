from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g
from app.models import db, User, Enrollment, Course, Competition, CompetitionParticipation, Certificate, ActivitySession
from app.utils.decorators import require_role

students_bp = Blueprint('students', __name__)

@students_bp.route('/api/teacher/students', methods=['GET'])
@require_role('teacher', 'admin')
def list_students():
    q = request.args.get('q', '').strip()
    course_id = request.args.get('course_id', type=int)
    comp_id = request.args.get('competition_id', type=int)
    activity_level = request.args.get('activity_level', '').strip()

    # Query members and students (Teachers only see students; Admins see all)
    query = User.query.filter(User.status == 'approved')

    is_admin = getattr(g.current_user, 'role', '') in ['admin', 'root_admin'] or getattr(g.current_user, 'is_root_admin', False)
    if not is_admin:
        query = query.filter(
            User.role.in_(['student', 'member']),
            User.role != 'teacher',
            User.role != 'admin',
            User.role != 'root_admin',
            User.is_root_admin == False
        )

    if q:
        search_pattern = f"%{q}%"
        query = query.filter(
            (User.username.ilike(search_pattern)) |
            (User.full_name.ilike(search_pattern)) |
            (User.email.ilike(search_pattern)) |
            (User.student_id.ilike(search_pattern))
        )

    if course_id:
        enrolled_user_ids = [e.user_id for e in Enrollment.query.filter_by(course_id=course_id).all()]
        query = query.filter(User.id.in_(enrolled_user_ids))

    if comp_id:
        comp_user_ids = [p.user_id for p in CompetitionParticipation.query.filter_by(competition_id=comp_id).all()]
        query = query.filter(User.id.in_(comp_user_ids))

    users = query.order_by(User.username.asc()).all()

    # Aggregate activity hours for filtering & display
    results = []
    thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')

    for u in users:
        sessions = ActivitySession.query.filter(
            ActivitySession.user_id == u.id,
            ActivitySession.date >= thirty_days_ago
        ).all()
        total_hours = round(sum(s.duration_seconds for s in sessions) / 3600.0, 1)

        level = 'low'
        if total_hours >= 20.0:
            level = 'high'
        elif total_hours >= 5.0:
            level = 'medium'

        if activity_level and activity_level != level:
            continue

        enrollments_count = Enrollment.query.filter_by(user_id=u.id).count()
        competitions_count = CompetitionParticipation.query.filter_by(user_id=u.id).count()

        u_dict = u.to_dict()
        u_dict['total_activity_hours'] = total_hours
        u_dict['activity_level'] = level
        u_dict['enrollments_count'] = enrollments_count
        u_dict['competitions_count'] = competitions_count
        results.append(u_dict)

    return jsonify({'students': results}), 200

@students_bp.route('/api/teacher/students/<int:user_id>', methods=['GET'])
@require_role('teacher', 'admin')
def get_student_profile(user_id):
    student = User.query.get_or_404(user_id)
    return jsonify(build_structured_profile(student)), 200

def build_structured_profile(user):
    """Builds the complete structured profile JSON (Overview, Activity, Academy, Competitions Trophy Case)"""
    # 1. Overview
    overview = user.to_dict()

    # 2. Activity Data
    thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
    sessions = ActivitySession.query.filter(
        ActivitySession.user_id == user.id,
        ActivitySession.date >= thirty_days_ago
    ).all()

    total_seconds = sum(s.duration_seconds for s in sessions)
    subdomain_map = {'club': 0, 'ctf': 0, 'intro': 0}
    daily_map = {}
    for i in range(30):
        d_str = (datetime.utcnow() - timedelta(days=29 - i)).strftime('%Y-%m-%d')
        daily_map[d_str] = 0.0

    for s in sessions:
        subdomain_map[s.subdomain] = subdomain_map.get(s.subdomain, 0) + s.duration_seconds
        if s.date in daily_map:
            daily_map[s.date] += round(s.duration_seconds / 3600.0, 2)

    activity = {
        'total_hours': round(total_seconds / 3600.0, 1),
        'subdomain_breakdown': {k: round(v / 3600.0, 1) for k, v in subdomain_map.items()},
        'chart_data': [{'date': d, 'hours': daily_map[d]} for d in sorted(daily_map.keys())]
    }

    # 3. Academy (Enrolled & Completed Courses + Certificates)
    enrollments = Enrollment.query.filter_by(user_id=user.id).all()
    academy_courses = []

    for e in enrollments:
        c = Course.query.get(e.course_id)
        if not c:
            continue
        cert = Certificate.query.filter_by(user_id=user.id, source_id=c.id, type='course_completion').first()
        academy_courses.append({
            'course_id': c.id,
            'title': c.title,
            'slug': c.slug,
            'cover_image': c.cover_image,
            'progress_percent': e.progress_percent,
            'completed_at': e.completed_at.isoformat() if e.completed_at else None,
            'certificate': cert.to_dict() if cert else None
        })

    # 4. Competitions ("Trophy Case")
    participations = CompetitionParticipation.query.filter_by(user_id=user.id).all()
    trophy_case = []

    for p in participations:
        comp = Competition.query.get(p.competition_id)
        if not comp:
            continue
        cert = Certificate.query.filter_by(user_id=user.id, source_id=comp.id, type='competition').first()
        trophy_case.append({
            'participation_id': p.id,
            'competition_id': comp.id,
            'competition_title': comp.title,
            'category': comp.category,
            'poster_image': comp.poster_image,
            'external_link': comp.external_link,
            'starts_at': comp.starts_at.isoformat() if comp.starts_at else None,
            'ends_at': comp.ends_at.isoformat() if comp.ends_at else None,
            'application_screenshot': p.application_screenshot,
            'application_status': p.application_status,
            'result': p.result,
            'placement_label': p.placement_label,
            'summary_notes': p.summary_notes,
            'event_photos': p.event_photos or [],
            'certificate': cert.to_dict() if cert else None
        })

    return {
        'overview': overview,
        'activity': activity,
        'academy': academy_courses,
        'trophy_case': trophy_case
    }
