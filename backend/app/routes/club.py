from flask import Blueprint, request, jsonify, g
from app.models import db, User, CourseEnrollment, CompetitionApplication, AuditLog, DeviceSession, ProfileFieldDefinition, UserProfileValue
from app.utils.decorators import require_auth, require_role, log_audit

club_bp = Blueprint('club', __name__, url_prefix='/api/club')

@club_bp.route('/stats', methods=['GET'])
@require_auth
def get_stats():
    total_members = User.query.filter_by(status='approved').count()
    active_courses = CourseEnrollment.query.count()
    completed_courses = CourseEnrollment.query.filter(CourseEnrollment.progress_percent >= 100.0).count()
    from app.models.moderation import SiteFeatureToggle
    toggle = SiteFeatureToggle.query.first()
    announcement_text = None
    if toggle and getattr(toggle, 'announcement_enabled', True):
        banner = (toggle.announcement_banner or '').strip()
        announcement_text = banner if banner else None

    return jsonify({
        'total_members': total_members,
        'active_courses': active_courses,
        'completed_courses': completed_courses,
        'ctf_rank': 12,
        'announcement': announcement_text
    }), 200

@club_bp.route('/members', methods=['GET'])
@require_auth
def get_members():
    query = User.query.filter_by(status='approved')
    
    is_admin = (g.current_user.role in ['admin', 'root_admin']) or getattr(g.current_user, 'is_root_admin', False)
    if g.current_user.role == 'teacher' and not is_admin:
        query = query.filter(User.role.in_(['student', 'member']))

    members = query.all()
    is_privileged = (g.current_user.role in ['teacher', 'admin', 'root_admin']) or getattr(g.current_user, 'is_root_admin', False)
    return jsonify({
        'members': [m.to_dict(include_private=(is_privileged or m.id == g.current_user.id), include_security=is_admin) for m in members]
    }), 200

@club_bp.route('/members/<int:member_id>', methods=['GET'])
@require_role('teacher', 'admin', 'root_admin')
def get_student_profile(member_id):
    student = User.query.get_or_404(member_id)
    enrollments = CourseEnrollment.query.filter_by(user_id=member_id).all()
    competition_apps = CompetitionApplication.query.filter_by(user_id=member_id).all()
    is_admin = (g.current_user.role in ['admin', 'root_admin']) or getattr(g.current_user, 'is_root_admin', False)

    log_audit('VIEW_STUDENT_PROFILE', target_type='User', target_id=member_id, details={'student_email': student.email})

    return jsonify({
        'student': student.to_dict(include_private=True, include_security=is_admin),
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
    if 'academic_year' in data:
        user.academic_year = data['academic_year']
    if 'department' in data:
        user.department = data['department']
    if 'graduation_year' in data:
        user.graduation_year = data['graduation_year']
    if 'skills' in data and isinstance(data['skills'], list):
        user.skills = data['skills']

    if 'gmail' in data: user.gmail = (data['gmail'] or '').strip()
    if 'personal_gmail' in data: user.personal_gmail = (data['personal_gmail'] or '').strip()
    if 'student_gmail' in data: user.student_gmail = (data['student_gmail'] or '').strip()
    if 'phone_number' in data: user.phone_number = (data['phone_number'] or '').strip()

    if 'resume_url' in data: user.resume_url = (data['resume_url'] or '').strip()
    if 'website_url' in data: user.website_url = (data['website_url'] or '').strip()
    if 'github_url' in data: user.github_url = (data['github_url'] or '').strip()
    if 'linkedin_url' in data: user.linkedin_url = (data['linkedin_url'] or '').strip()
    if 'tryhackme_url' in data: user.tryhackme_url = (data['tryhackme_url'] or '').strip()
    if 'htb_url' in data: user.htb_url = (data['htb_url'] or '').strip()

    db.session.commit()

    # Sync user details to CTFd container
    try:
        from app.services.ctfd_sync import sync_user_to_ctfd
        sync_user_to_ctfd(user)
    except Exception as e:
        print(f"CTFd profile sync note: {e}")

    log_audit('UPDATE_PROFILE', target_type='User', target_id=user.id, target_user_id=user.id)
    return jsonify(user.to_dict(include_private=True)), 200

@club_bp.route('/profile/resume', methods=['DELETE'])
@require_auth
def delete_resume():
    """Deletes the user's uploaded resume file from disk and clears the DB field."""
    import os
    user = g.current_user
    if not user.resume_url:
        return jsonify({'message': 'No resume on file.'}), 200

    # Attempt physical file deletion
    upload_base = '/var/uploads'
    rel_path = user.resume_url.lstrip('/')           # e.g. uploads/resumes/abc123.pdf
    abs_path = os.path.join(upload_base, rel_path.replace('uploads/', '', 1))
    try:
        if os.path.isfile(abs_path):
            os.remove(abs_path)
    except Exception as e:
        print(f"Resume file delete warning: {e}")

    user.resume_url = None
    db.session.commit()

    log_audit('RESUME_DELETED', target_type='User', target_id=user.id, target_user_id=user.id)
    return jsonify({'message': 'Resume removed successfully.'}), 200

# -------------------------------------------------------------------
# Device & Session Management (/profile/devices) - All Roles
# -------------------------------------------------------------------
@club_bp.route('/profile/devices', methods=['GET'])
@require_auth
def list_my_devices():
    sessions = DeviceSession.query.filter_by(user_id=g.current_user.id, is_active=True).order_by(DeviceSession.created_at.desc()).all()
    current_session_id = g.current_session.id if g.current_session else None

    res = []
    for s in sessions:
        d = s.to_dict()
        d['is_current_device'] = (s.id == current_session_id)
        res.append(d)

    return jsonify({'devices': res}), 200

@club_bp.route('/profile/devices/<int:session_id>', methods=['DELETE'])
@require_auth
def revoke_my_device(session_id):
    sess = DeviceSession.query.filter_by(id=session_id, user_id=g.current_user.id).first_or_404()
    sess.is_active = False
    db.session.commit()

    log_audit('REVOKE_DEVICE_SESSION', target_type='DeviceSession', target_id=session_id, target_user_id=g.current_user.id)
    return jsonify({'message': 'Device logged out successfully'}), 200

@club_bp.route('/profile/devices/others', methods=['DELETE'])
@require_auth
def logout_all_other_devices():
    current_id = g.current_session.id if g.current_session else None
    query = DeviceSession.query.filter_by(user_id=g.current_user.id, is_active=True)
    if current_id:
        query = query.filter(DeviceSession.id != current_id)
    
    count = query.update({'is_active': False})
    db.session.commit()

    log_audit('LOGOUT_ALL_OTHER_DEVICES', target_type='User', target_id=g.current_user.id, target_user_id=g.current_user.id, notes=f"Revoked {count} other sessions")
    return jsonify({'message': f'Logged out {count} other devices successfully'}), 200

@club_bp.route('/profile/devices/tools', methods=['DELETE'])
@require_auth
def revoke_tool_sessions():
    """Revoke all sessions from non-browser clients (curl, Werkzeug, Python-urllib, etc.)"""
    TOOL_AGENTS = ('curl/', 'Werkzeug/', 'Python-urllib/', 'python-requests/', 'httpie/')
    sessions = DeviceSession.query.filter_by(user_id=g.current_user.id, is_active=True).all()
    count = 0
    for s in sessions:
        if any(s.user_agent.startswith(agent) for agent in TOOL_AGENTS if s.user_agent):
            s.is_active = False
            count += 1
    db.session.commit()
    log_audit('REVOKE_TOOL_SESSIONS', target_type='User', target_id=g.current_user.id, target_user_id=g.current_user.id, notes=f"Purged {count} tool/API sessions")
    return jsonify({'message': f'Revoked {count} tool/API sessions.', 'count': count}), 200

# -------------------------------------------------------------------
# Missing Custom Profile Fields Check
# -------------------------------------------------------------------
@club_bp.route('/profile/missing-fields', methods=['GET'])
@require_auth
def get_missing_required_fields():
    user = g.current_user
    user_role = user.role
    
    query = ProfileFieldDefinition.query.filter_by(active=True, required=True)
    if user_role == 'member':
        query = query.filter(ProfileFieldDefinition.target_role.in_(['all', 'member']))
    elif user_role in ['teacher', 'instructor']:
        query = query.filter(ProfileFieldDefinition.target_role.in_(['all', 'teacher']))
        
    active_required_fields = query.all()
    user_values = UserProfileValue.query.filter_by(user_id=user.id).all()
    filled_field_ids = {v.field_id for v in user_values if v.value and v.value.strip()}

    missing = [f.to_dict() for f in active_required_fields if f.id not in filled_field_ids]
    return jsonify({'missing_fields': missing}), 200

@club_bp.route('/profile/values', methods=['POST'])
@require_auth
def save_profile_values():
    data = request.get_json() or {} # dict of {field_id_or_key: value}
    user_id = g.current_user.id

    active_fields = ProfileFieldDefinition.query.filter_by(active=True).all()
    for field in active_fields:
        val = data.get(str(field.id)) or data.get(field.field_key)
        if val is not None:
            pv = UserProfileValue.query.filter_by(user_id=user_id, field_id=field.id).first()
            if pv:
                pv.value = str(val)
            else:
                pv = UserProfileValue(user_id=user_id, field_id=field.id, value=str(val))
                db.session.add(pv)
    db.session.commit()
    return jsonify({'message': 'Profile fields updated successfully'}), 200
