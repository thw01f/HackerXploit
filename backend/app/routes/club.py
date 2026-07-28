from flask import Blueprint, request, jsonify, g
from app.models import db, User, CourseEnrollment, CompetitionApplication, AuditLog
from app.utils.decorators import require_auth, require_role, log_audit

club_bp = Blueprint('club', __name__, url_prefix='/api/club')

@club_bp.route('/stats', methods=['GET'])
@require_auth
def get_stats():
    total_members = User.query.filter_by(status='approved').count()
    active_courses = CourseEnrollment.query.count()
    completed_courses = CourseEnrollment.query.filter_by(is_completed=True).count()
    return jsonify({
        'total_members': total_members,
        'active_courses': active_courses,
        'completed_courses': completed_courses,
        'ctf_rank': 12, # Dynamic placeholder or CTFd score integration
        'announcement': 'Welcome to HackerXploit Club Platform! Next CTF competition is scheduled for Saturday.'
    }), 200

@club_bp.route('/members', methods=['GET'])
@require_auth
def get_members():
    members = User.query.filter_by(status='approved').all()
    return jsonify({'members': [m.to_dict() for m in members]}), 200

@club_bp.route('/members/<int:member_id>', methods=['GET'])
@require_role('teacher', 'admin', 'root_admin')
def get_student_profile(member_id):
    student = User.query.get_or_404(member_id)
    enrollments = CourseEnrollment.query.filter_by(user_id=member_id).all()
    competition_apps = CompetitionApplication.query.filter_by(user_id=member_id).all()

    # Log audit entry when viewing student details (teacher/admin requirement)
    log_audit('VIEW_STUDENT_PROFILE', target_type='User', target_id=member_id, details={'student_email': student.email})

    return jsonify({
        'student': student.to_dict(),
        'enrollments': [e.to_dict() for e in enrollments],
        'competitions': [c.to_dict() for c in competition_apps],
        'estimated_learning_hours': len(enrollments) * 8 + len(competition_apps) * 5
    }), 200

@club_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    data = request.get_json() or {}
    user = g.current_user

    if 'full_name' in data:
        user.full_name = data['full_name'].strip()
    if 'bio' in data:
        user.bio = data['bio'].strip()
    if 'avatar_url' in data:
        user.avatar_url = data['avatar_url']
    if 'student_id' in data:
        user.student_id = data['student_id']
    if 'graduation_year' in data:
        user.graduation_year = data['graduation_year']
    if 'skills' in data and isinstance(data['skills'], list):
        user.skills = data['skills']

    db.session.commit()
    log_audit('UPDATE_PROFILE', target_type='User', target_id=user.id)
    return jsonify(user.to_dict()), 200
