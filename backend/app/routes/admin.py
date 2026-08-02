import secrets
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g, current_app
from app.models import db, User, DeviceSession, LoginAttempt, AuditLog, PasswordResetRequest, PasswordResetCode, ProfileFieldDefinition, NotificationPreference
from app.utils.decorators import require_auth, require_role, require_root, log_audit
from app.services.ctfd_sync import sync_user_to_ctfd, delete_user_from_ctfd
from app.services.email_service import send_account_status_email, send_announcement_email

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def _dispatch_email_task(task, *args):
    """Runs a celery-decorated email task synchronously in tests, async otherwise."""
    try:
        if current_app.config.get('TESTING'):
            task(*args)
        else:
            task.delay(*args)
    except Exception as e:
        print(f"Email dispatch note: {e}")


def _maybe_send_status_email(user, status):
    if NotificationPreference.get_or_create(user.id).email_account_updates:
        _dispatch_email_task(send_account_status_email, user.id, status)


def _maybe_send_announcement_email(user, title, message):
    if NotificationPreference.get_or_create(user.id).email_announcements:
        _dispatch_email_task(send_announcement_email, user.id, title, message)

# -------------------------------------------------------------------
# 1. Approval Workflow (/admin/users) - Admin & Teacher allowed
# -------------------------------------------------------------------
@admin_bp.route('/users', methods=['GET'])
@require_role('teacher', 'admin')
def list_users():
    status = request.args.get('status')
    search = (request.args.get('search') or '').strip()
    query = User.query
    if status:
        query = query.filter_by(status=status)
    if search:
        like = f"%{search}%"
        query = query.filter(db.or_(User.username.ilike(like), User.full_name.ilike(like), User.email.ilike(like)))

    is_admin = getattr(g.current_user, 'role', '') in ['admin', 'root_admin'] or getattr(g.current_user, 'is_root_admin', False)
    if not is_admin:
        query = query.filter(User.role.in_(['student', 'member']))

    users = query.order_by(User.created_at.desc()).all()
    return jsonify({'users': [u.to_dict(include_security=is_admin) for u in users]}), 200

@admin_bp.route('/users/<int:user_id>/approve', methods=['POST'])
@require_role('teacher', 'admin')
def approve_user(user_id):
    data = request.get_json(silent=True) or {}
    user = User.query.get_or_404(user_id)
    
    is_admin = getattr(g.current_user, 'role', '') in ['admin', 'root_admin'] or getattr(g.current_user, 'is_root_admin', False)
    
    # Teachers can only approve students
    if not is_admin:
        user.role = 'member'
    else:
        assigned_role = data.get('assigned_role')
        if assigned_role in ['member', 'teacher', 'admin']:
            user.role = assigned_role

    user.status = 'approved'
    user.is_first_login = True
    user.onboarding_completed = False
    user.approved_by = g.current_user.id
    user.approved_at = datetime.utcnow()
    db.session.commit()

    # Auto-provision user into CTFd database
    try:
        from app.services.ctfd_sync import sync_user_to_ctfd
        sync_user_to_ctfd(user)
    except Exception as e:
        print(f"CTFd auto-provision note: {e}")

    _maybe_send_status_email(user, 'approved')

    log_audit('approved', target_type='User', target_id=user_id, target_user_id=user_id, notes=f"Approved as {user.role} by {g.current_user.username}")
    return jsonify(user.to_dict()), 200

@admin_bp.route('/users/<int:user_id>/reject', methods=['POST'])
@require_role('teacher', 'admin')
def reject_user(user_id):
    user = User.query.get_or_404(user_id)
    is_admin = getattr(g.current_user, 'role', '') in ['admin', 'root_admin'] or getattr(g.current_user, 'is_root_admin', False)
    if not is_admin and user.role not in ['student', 'member']:
        return jsonify({'error': 'Teachers can only manage student accounts'}), 403

    if user.is_root_admin:
        return jsonify({'error': 'Root admin cannot be rejected'}), 403

    user.status = 'rejected'
    db.session.commit()

    _maybe_send_status_email(user, 'rejected')

    log_audit('rejected', target_type='User', target_id=user_id, target_user_id=user_id, notes=f"Rejected by {g.current_user.username}")
    return jsonify(user.to_dict()), 200

@admin_bp.route('/users/<int:user_id>/suspend', methods=['POST'])
@require_role('teacher', 'admin')
def suspend_user(user_id):
    user = User.query.get_or_404(user_id)
    is_admin = getattr(g.current_user, 'role', '') in ['admin', 'root_admin'] or getattr(g.current_user, 'is_root_admin', False)
    if not is_admin and user.role not in ['student', 'member']:
        return jsonify({'error': 'Teachers can only manage student accounts'}), 403

    if user.is_root_admin:
        return jsonify({'error': 'Root Admin cannot be suspended'}), 403

    user.status = 'suspended'
    
    # KILL-SWITCH: Invalidate all live device sessions immediately
    DeviceSession.query.filter_by(user_id=user_id, is_active=True).update({'is_active': False})
    db.session.commit()

    _maybe_send_status_email(user, 'suspended')

    log_audit('suspended', target_type='User', target_id=user_id, target_user_id=user_id, notes=f"Suspended by {g.current_user.username}")
    return jsonify(user.to_dict()), 200

@admin_bp.route('/users/<int:user_id>/reinstate', methods=['POST'])
@require_role('teacher', 'admin')
def reinstate_user(user_id):
    user = User.query.get_or_404(user_id)
    is_admin = getattr(g.current_user, 'role', '') in ['admin', 'root_admin'] or getattr(g.current_user, 'is_root_admin', False)
    if not is_admin and user.role not in ['student', 'member']:
        return jsonify({'error': 'Teachers can only manage student accounts'}), 403

    user.status = 'approved'
    db.session.commit()

    log_audit('reinstated', target_type='User', target_id=user_id, target_user_id=user_id, notes=f"Reinstated by {g.current_user.username}")
    return jsonify(user.to_dict()), 200

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_role('admin')
def delete_user_account(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_root_admin:
        return jsonify({'error': 'Root Admin account cannot be deleted'}), 403
    if user.id == g.current_user.id:
        return jsonify({'error': 'You cannot delete your own active admin account'}), 400

    username = user.username
    email = user.email
    # Terminate sessions
    DeviceSession.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()

    # Automatically purge user from CTFd
    delete_user_from_ctfd(username, email)

    log_audit('USER_DELETED', target_type='User', target_id=user_id, notes=f"User @{username} permanently deleted by {g.current_user.username}")
    return jsonify({'message': f'User @{username} deleted successfully'}), 200

@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@require_role('admin')
def admin_force_reset_password(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    new_password = data.get('new_password', '').strip()

    if not new_password or len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400

    user.set_password(new_password)
    # Invalidate existing active sessions to force re-authentication
    DeviceSession.query.filter_by(user_id=user_id, is_active=True).update({'is_active': False})
    db.session.commit()

    log_audit('ADMIN_PASSWORD_RESET', target_type='User', target_id=user_id, notes=f"Password for @{user.username} reset by Admin {g.current_user.username}")
    return jsonify({'message': f'Password for @{user.username} has been reset successfully'}), 200

@admin_bp.route('/users/<int:user_id>/update', methods=['PUT'])
@require_role('teacher', 'admin')
def update_user_details(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}

    is_admin = getattr(g.current_user, 'role', '') in ['admin', 'root_admin'] or getattr(g.current_user, 'is_root_admin', False)

    # Non-admin teachers can only edit student / member accounts
    if not is_admin and user.role not in ['student', 'member']:
        return jsonify({'error': 'Teachers can only edit student accounts'}), 403

    if 'full_name' in data and data['full_name']:
        user.full_name = data['full_name'].strip()
    if 'email' in data and data['email']:
        user.email = data['email'].strip()
    if 'student_id' in data:
        user.student_id = data['student_id'].strip() if data['student_id'] else None
    if 'specialization_role' in data:
        user.specialization_role = data['specialization_role'].strip() if data['specialization_role'] else 'Penetration Tester'
    if 'total_points' in data:
        try:
            user.total_points = int(data['total_points'])
        except (ValueError, TypeError):
            pass

    if 'role' in data:
        new_role = data['role']
        if is_admin:
            if new_role in ['student', 'member', 'teacher', 'admin']:
                user.role = new_role
                user.badge_id = None # Forces recalculation of Badge ID with new role prefix (e.g. HX-FAC-0001 or HX-ADM-0001)
        else:
            if new_role in ['student', 'member']:
                user.role = new_role
                user.badge_id = None

    if 'status' in data:
        if is_admin or user.role in ['student', 'member']:
            user.status = data['status']

    # Recalculate badge_id for response
    user.badge_id = user.get_badge_id()
    db.session.commit()

    # Instant CTFd role & badge sync
    try:
        from app.services.ctfd_sync import sync_user_to_ctfd
        sync_user_to_ctfd(user)
    except Exception as e:
        print(f"[CTFd Sync Error on Role Update]: {e}")

    log_audit('USER_DETAILS_UPDATED', target_type='User', target_id=user_id, notes=f"Updated details for @{user.username} (Role: {user.role}, Badge: {user.badge_id}) by {g.current_user.username}")
    return jsonify(user.to_dict()), 200

# -------------------------------------------------------------------
# 2. Site-wide Audit Log (/admin/audit-log) - View: teacher+; Delete: admin only
# -------------------------------------------------------------------
@admin_bp.route('/audit-log', methods=['GET'])
@require_role('teacher', 'admin')
def get_audit_log():
    actor_id = request.args.get('actor_id')
    action = request.args.get('action')

    query = AuditLog.query
    if actor_id and actor_id.isdigit():
        query = query.filter_by(actor_id=int(actor_id))
    if action:
        query = query.filter_by(action=action)

    logs = query.order_by(AuditLog.created_at.desc()).limit(200).all()
    return jsonify({'audit_logs': [l.to_dict() for l in logs]}), 200

@admin_bp.route('/audit-log', methods=['DELETE'])
@require_role('admin')
def clear_audit_log_history():
    # Bulk clear audit logs
    count = AuditLog.query.delete()
    db.session.commit()

    log_audit('AUDIT_LOG_BULK_CLEARED', notes=f"Cleared {count} audit log entries")
    return jsonify({'message': f'Cleared {count} audit log entries'}), 200

@admin_bp.route('/audit-log/<int:log_id>', methods=['DELETE'])
@require_role('admin')
def delete_audit_log_entry(log_id):
    entry = AuditLog.query.get_or_404(log_id)
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Audit log entry deleted'}), 200

# -------------------------------------------------------------------
# 3. Security Login Activity & Manual Unlock - Admin only
# -------------------------------------------------------------------
@admin_bp.route('/security/login-activity', methods=['GET'])
@require_role('admin')
def get_login_activity():
    username = request.args.get('username')
    success = request.args.get('success')

    query = LoginAttempt.query
    if username:
        query = query.filter(LoginAttempt.username_attempted.ilike(f"%{username}%"))
    if success is not None:
        is_success = success.lower() in ['true', '1']
        query = query.filter_by(success=is_success)

    activities = query.order_by(LoginAttempt.created_at.desc()).limit(150).all()
    return jsonify({'activities': [a.to_dict() for a in activities]}), 200

@admin_bp.route('/security/login-activity/<int:user_id>/unlock', methods=['POST'])
@require_role('admin')
def manual_unlock_user(user_id):
    user = User.query.get_or_404(user_id)
    user.locked_until = None
    user.failed_login_count = 0
    db.session.commit()

    log_audit('manual_unlock', target_type='User', target_id=user_id, target_user_id=user_id, notes=f"Manually unlocked by {g.current_user.username}")
    return jsonify({'message': f'User {user.username} unlocked successfully', 'user': user.to_dict(include_security=True)}), 200

# -------------------------------------------------------------------
# 4. Admin-Issued Password Reset (/admin/password-requests) - Admin only
# -------------------------------------------------------------------
@admin_bp.route('/password-requests', methods=['GET'])
@require_role('admin')
def list_password_requests():
    requests = PasswordResetRequest.query.filter_by(status='pending').order_by(PasswordResetRequest.created_at.desc()).all()
    res = []
    for r in requests:
        user = User.query.get(r.user_id)
        d = r.to_dict()
        d['username'] = user.username if user else 'Unknown'
        d['email'] = user.email if user else 'Unknown'
        res.append(d)
    return jsonify({'requests': res}), 200

@admin_bp.route('/password-requests/generate', methods=['POST'])
@require_role('admin')
def generate_password_reset_code():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    user = User.query.get_or_404(user_id)

    # Generate random 8-character uppercase alphanumeric code
    code = secrets.token_hex(4).upper()
    expires_at = datetime.utcnow() + timedelta(minutes=3)

    reset_code = PasswordResetCode(
        user_id=user.id,
        code=code,
        issued_by_admin_id=g.current_user.id,
        expires_at=expires_at
    )
    db.session.add(reset_code)
    db.session.commit()

    log_audit('PASSWORD_RESET_CODE_ISSUED', target_type='User', target_id=user.id, target_user_id=user.id, notes=f"Issued code {code} expiring in 3m")

    return jsonify({
        'message': 'Password reset code generated successfully',
        'code': code,
        'expires_at': expires_at.isoformat(),
        'user': user.to_dict()
    }), 201

# -------------------------------------------------------------------
# 5. Admin Hierarchy (/admin/manage-admins) - Root Admin Only
# -------------------------------------------------------------------
@admin_bp.route('/users/<int:user_id>/role', methods=['POST'])
@require_root
def change_user_role(user_id):
    data = request.get_json() or {}
    new_role = data.get('role')

    allowed_roles = {'admin', 'teacher', 'member'}
    if new_role not in allowed_roles:
        return jsonify({'error': 'Invalid role specified'}), 400

    user = User.query.get_or_404(user_id)
    if user.is_root_admin:
        return jsonify({'error': 'Cannot change Root Admin role directly. Use transfer root.'}), 403

    # Enforce Hard Cap of 5 Non-Root Admins
    if new_role == 'admin':
        non_root_admin_count = User.query.filter_by(role='admin', is_root_admin=False).count()
        if non_root_admin_count >= 5:
            return jsonify({'error': 'Admin limit reached: Maximum 5 non-root admins permitted'}), 400

    old_role = user.role
    user.role = new_role
    db.session.commit()

    log_audit('role_changed', target_type='User', target_id=user_id, target_user_id=user_id, notes=f"Role changed from {old_role} to {new_role}")
    return jsonify(user.to_dict()), 200

@admin_bp.route('/transfer-root', methods=['POST'])
@require_root
def transfer_root():
    data = request.get_json() or {}
    target_user_id = data.get('target_user_id')

    target_user = User.query.get_or_404(target_user_id)
    current_root = g.current_user

    current_root.is_root_admin = False
    current_root.role = 'admin'

    target_user.is_root_admin = True
    target_user.role = 'admin'
    target_user.status = 'approved'
    db.session.commit()

    log_audit('TRANSFER_ROOT_STATUS', target_type='User', target_id=target_user_id, target_user_id=target_user_id, notes=f"Root admin transferred to {target_user.username}")
    return jsonify({'message': f'Root admin status transferred to {target_user.username}'}), 200

@admin_bp.route('/users/<int:user_id>/promote-teacher', methods=['POST'])
@require_role('admin')
def promote_to_teacher(user_id):
    data = request.get_json() or {}
    user = User.query.get_or_404(user_id)

    department = data.get('department', '').strip()
    designation = data.get('designation', '').strip()
    staff_id = data.get('staff_id', '').strip()
    notes = data.get('notes', '').strip()

    user.role = 'teacher'
    user.status = 'approved'
    
    if department:
        user.bio = f"Department: {department} | Designation: {designation or 'Faculty Member'}"
    if staff_id:
        user.student_id = staff_id

    # Create Notification for the user
    try:
        from app.models.chat import Notification
        notif = Notification(
            user_id=user.id,
            type='system',
            title='🎓 Faculty Role Assigned',
            message=f'Administrator promoted you to Faculty/Teacher status. Department: {department or "General"}. Welcome to the Faculty team!',
            link='/teacher/students'
        )
        db.session.add(notif)
    except Exception as e:
        print(f"Notification error: {e}")

    db.session.commit()

    _maybe_send_announcement_email(
        user,
        'Faculty Role Assigned',
        f'An administrator promoted you to Faculty/Teacher status. Department: {department or "General"}. Welcome to the Faculty team!'
    )

    log_audit('PROMOTE_TEACHER', target_type='User', target_id=user.id, target_user_id=user.id, notes=f"Promoted {user.username} to teacher. Dept: {department}, Staff ID: {staff_id}")
    return jsonify({
        'message': f'User {user.username} promoted to Teacher successfully',
        'user': user.to_dict()
    }), 200

# -------------------------------------------------------------------
# 6. Flexible Custom Profile Fields (/admin/profile-fields) - Admin Only
# -------------------------------------------------------------------
@admin_bp.route('/profile-fields', methods=['GET'])
@require_role('admin')
def list_profile_fields():
    fields = ProfileFieldDefinition.query.order_by(ProfileFieldDefinition.id.asc()).all()
    return jsonify({'fields': [f.to_dict() for f in fields]}), 200

@admin_bp.route('/profile-fields', methods=['POST'])
@require_role('admin')
def create_profile_field():
    data = request.get_json() or {}
    field_key = data.get('field_key', '').strip().lower().replace(' ', '_')
    label = data.get('label', '').strip()
    field_type = data.get('field_type', 'text')
    options = data.get('options', [])
    target_role = data.get('target_role', 'all')
    required = bool(data.get('required', False))

    if not field_key or not label:
        return jsonify({'error': 'field_key and label are required'}), 400

    if ProfileFieldDefinition.query.filter_by(field_key=field_key).first():
        return jsonify({'error': 'Field key already exists'}), 409

    pf = ProfileFieldDefinition(
        field_key=field_key,
        label=label,
        field_type=field_type,
        options=options,
        target_role=target_role,
        required=required,
        active=True,
        created_by=g.current_user.id
    )
    db.session.add(pf)
    db.session.commit()

    # Dispatch automatic notifications based on target_role
    notified_count = 0
    try:
        from app.models.chat import Notification
        query = User.query.filter_by(status='approved')
        if target_role == 'member':
            query = query.filter_by(role='member')
        elif target_role == 'teacher':
            query = query.filter(User.role.in_(['teacher', 'instructor']))
        elif target_role == 'all':
            query = query.filter(User.role.in_(['member', 'teacher', 'instructor', 'admin']))

        target_users = query.all()
        target_label = "Members" if target_role == 'member' else "Teachers/Faculty" if target_role == 'teacher' else "All Platform Users"

        for u in target_users:
            notif = Notification(
                user_id=u.id,
                type='system',
                title=f'📢 Action Required: New Profile Field Added',
                message=f'Administrator added a new profile field ({label}) for {target_label}. Please update your Profile Settings.',
                link='/profile'
            )
            db.session.add(notif)
            notified_count += 1

        db.session.commit()

        for u in target_users:
            _maybe_send_announcement_email(
                u,
                'New Profile Field Added',
                f'A new profile field ({label}) was added for {target_label}. Please update your Profile Settings.'
            )
    except Exception as e:
        print(f"Notification dispatch warning: {e}")

    log_audit('PROFILE_FIELD_CREATED', target_type='ProfileFieldDefinition', target_id=pf.id, notes=f"Created custom profile field {field_key} targeting {target_role} ({notified_count} notified)")

    result = pf.to_dict()
    result['notified_count'] = notified_count
    return jsonify(result), 201

@admin_bp.route('/profile-fields/<int:field_id>', methods=['PUT'])
@require_role('admin')
def update_profile_field(field_id):
    pf = ProfileFieldDefinition.query.get_or_404(field_id)
    data = request.get_json() or {}
    
    if 'label' in data:
        pf.label = data['label'].strip()
    if 'field_type' in data:
        pf.field_type = data['field_type']
    if 'options' in data:
        pf.options = data['options']
    if 'target_role' in data:
        pf.target_role = data['target_role']
    if 'required' in data:
        pf.required = bool(data['required'])
    if 'active' in data:
        pf.active = bool(data['active'])

    db.session.commit()
    log_audit('PROFILE_FIELD_UPDATED', target_type='ProfileFieldDefinition', target_id=field_id, notes=f"Updated profile field {pf.field_key}")
    return jsonify(pf.to_dict()), 200

@admin_bp.route('/profile-fields/<int:field_id>', methods=['DELETE'])
@require_role('admin')
def delete_profile_field(field_id):
    pf = ProfileFieldDefinition.query.get_or_404(field_id)
    key = pf.field_key
    db.session.delete(pf)
    db.session.commit()
    log_audit('PROFILE_FIELD_DELETED', target_type='ProfileFieldDefinition', target_id=field_id, notes=f"Deleted profile field {key}")
    return jsonify({'message': f'Profile field {key} deleted successfully'}), 200

# -------------------------------------------------------------------
# 7. Admin Session Force-Kick (/admin/security/sessions) - Admin Only
# -------------------------------------------------------------------
@admin_bp.route('/security/sessions', methods=['GET'])
@require_role('admin')
def search_member_sessions():
    username = request.args.get('username')
    user_id = request.args.get('user_id')

    query = DeviceSession.query.filter_by(is_active=True)

    if user_id and user_id.isdigit():
        query = query.filter_by(user_id=int(user_id))
    elif username:
        user = User.query.filter(User.username.ilike(f"%{username}%")).first()
        if user:
            query = query.filter_by(user_id=user.id)
        else:
            return jsonify({'sessions': []}), 200

    sessions = query.order_by(DeviceSession.created_at.desc()).all()
    res = []
    for s in sessions:
        u = User.query.get(s.user_id)
        d = s.to_dict()
        d['username'] = u.username if u else 'Unknown'
        res.append(d)

    return jsonify({'sessions': res}), 200

@admin_bp.route('/security/sessions/user/<int:user_id>', methods=['DELETE'])
@require_role('admin')
def force_kick_user_sessions(user_id):
    user = User.query.get_or_404(user_id)
    count = DeviceSession.query.filter_by(user_id=user_id, is_active=True).update({'is_active': False})
    db.session.commit()

    log_audit('FORCE_KICK_ALL_SESSIONS', target_type='User', target_id=user_id, target_user_id=user_id, notes=f"Kicked {count} active sessions for {user.username}")
    return jsonify({'message': f'Kicked {count} active sessions for {user.username}'}), 200

@admin_bp.route('/security/sessions/<int:session_id>', methods=['DELETE'])
@require_role('admin')
def force_kick_single_session(session_id):
    sess = DeviceSession.query.get_or_404(session_id)
    sess.is_active = False
    db.session.commit()

    log_audit('FORCE_KICK_SESSION', target_type='DeviceSession', target_id=session_id, target_user_id=sess.user_id, notes=f"Kicked session #{session_id}")
    return jsonify({'message': 'Session invalidated successfully'}), 200

# -------------------------------------------------------------------
# 8. Retention Settings & Competition Management - Admin Only
# -------------------------------------------------------------------
@admin_bp.route('/retention', methods=['GET'])
@require_role('admin')
def get_retention_settings():
    from app.models import RetentionSettings
    settings = RetentionSettings.query.first()
    if not settings:
        settings = RetentionSettings(competitions_auto_delete='never', competitions_delete_mode='archive')
        db.session.add(settings)
        db.session.commit()
    return jsonify(settings.to_dict()), 200

@admin_bp.route('/retention', methods=['POST'])
@require_role('admin')
def update_retention_settings():
    from app.models import RetentionSettings
    data = request.get_json() or {}
    auto_delete = data.get('competitions_auto_delete', 'never')
    delete_mode = data.get('competitions_delete_mode', 'archive')

    valid_auto = {'never', '1_month', '3_month', '6_month'}
    valid_mode = {'hard_delete', 'archive'}

    if auto_delete not in valid_auto or delete_mode not in valid_mode:
        return jsonify({'error': 'Invalid retention setting parameters'}), 400

    settings = RetentionSettings.query.first()
    if not settings:
        settings = RetentionSettings()
        db.session.add(settings)

    settings.competitions_auto_delete = auto_delete
    settings.competitions_delete_mode = delete_mode
    settings.updated_by_id = g.current_user.id
    db.session.commit()

    log_audit('RETENTION_SETTINGS_UPDATED', notes=f"Auto-delete: {auto_delete}, Delete mode: {delete_mode}")
    return jsonify(settings.to_dict()), 200

@admin_bp.route('/competitions/clear-history', methods=['POST'])
@require_role('admin')
def clear_competition_history():
    from app.models import Competition, RetentionSettings
    settings = RetentionSettings.query.first()
    mode = settings.competitions_delete_mode if settings else 'archive'

    ended_comps = Competition.query.filter_by(status='ended', is_archived=False).all()
    count = len(ended_comps)

    for c in ended_comps:
        if mode == 'hard_delete':
            db.session.delete(c)
        else:
            c.is_archived = True

    db.session.commit()

    log_audit('COMPETITION_HISTORY_CLEARED', notes=f"Cleared {count} competitions with mode '{mode}'")
    return jsonify({'message': f'Processed {count} ended competitions using mode: {mode}', 'count': count}), 200

@admin_bp.route('/competitions/<int:comp_id>', methods=['DELETE'])
@require_role('admin')
def delete_single_competition(comp_id):
    from app.models import Competition, RetentionSettings
    comp = Competition.query.get_or_404(comp_id)

    mode = request.args.get('mode')
    if not mode:
        settings = RetentionSettings.query.first()
        mode = settings.competitions_delete_mode if settings else 'archive'

    if mode == 'hard_delete':
        db.session.delete(comp)
        msg = "Competition deleted permanently"
    else:
        comp.is_archived = True
        msg = "Competition archived"

    db.session.commit()
    log_audit('COMPETITION_DELETED', target_type='Competition', target_id=comp_id, notes=f"Mode: {mode}")
    return jsonify({'message': msg}), 200

# -------------------------------------------------------------------
# 9. System & Member Analytics (/admin/analytics) - Admin Only
# -------------------------------------------------------------------
@admin_bp.route('/analytics', methods=['GET'])
@require_role('admin')
def get_admin_analytics():
    from app.models import Course, Enrollment, Competition, CompetitionParticipation, ActivitySession

    now = datetime.utcnow()

    # 1. Registration Trend (Totals & 30-Day)
    total_approved = User.query.filter_by(status='approved').count()
    total_pending = User.query.filter_by(status='pending').count()
    total_rejected = User.query.filter_by(status='rejected').count()
    total_suspended = User.query.filter_by(status='suspended').count()

    thirty_days_ago = now - timedelta(days=30)
    recent_signups = User.query.filter(User.created_at >= thirty_days_ago).count()

    # 2. Weekly Active Members (Last 8 Weeks)
    weekly_active = []
    for i in range(8):
        week_end = now - timedelta(days=i * 7)
        week_start = week_end - timedelta(days=7)
        active_count = db.session.query(ActivitySession.user_id).filter(
            ActivitySession.created_at >= week_start,
            ActivitySession.created_at < week_end
        ).distinct().count()

        # Fallback to User.last_login_at if activity sessions haven't rolled up yet
        if active_count == 0:
            active_count = User.query.filter(
                User.last_login_at >= week_start,
                User.last_login_at < week_end
            ).count()

        weekly_active.append({
            'week': f"W-{7-i}",
            'label': week_start.strftime('%b %d'),
            'active_members': active_count
        })
    weekly_active.reverse()

    # 3. Top 5 Courses by Enrollment
    top_courses_query = db.session.query(
        Course.id, Course.title, Course.slug, db.func.count(Enrollment.id).label('enrollment_count')
    ).join(Enrollment, Course.id == Enrollment.course_id, isouter=True)\
     .group_by(Course.id)\
     .order_by(db.desc('enrollment_count'))\
     .limit(5).all()

    top_courses = [{
        'id': c.id,
        'title': c.title,
        'slug': c.slug,
        'enrollment_count': c.enrollment_count
    } for c in top_courses_query]

    # 4. Top 5 Competitions by Participation
    top_comps_query = db.session.query(
        Competition.id, Competition.title, Competition.category, db.func.count(CompetitionParticipation.id).label('participant_count')
    ).join(CompetitionParticipation, Competition.id == CompetitionParticipation.competition_id, isouter=True)\
     .group_by(Competition.id)\
     .order_by(db.desc('participant_count'))\
     .limit(5).all()

    top_competitions = [{
        'id': comp.id,
        'title': comp.title,
        'category': comp.category,
        'participant_count': comp.participant_count
    } for comp in top_comps_query]

    return jsonify({
        'registration_trend': {
            'total_approved': total_approved,
            'total_pending': total_pending,
            'total_rejected': total_rejected,
            'total_suspended': total_suspended,
            'recent_30_day_signups': recent_signups
        },
        'weekly_active_members': weekly_active,
        'top_courses': top_courses,
        'top_competitions': top_competitions
    }), 200

@admin_bp.route('/settings', methods=['GET'])
@require_role('admin')
def get_site_settings():
    from app.models import SiteFeatureToggle
    toggle = SiteFeatureToggle.query.first()
    if not toggle:
        toggle = SiteFeatureToggle(general_chat_enabled=True)
        db.session.add(toggle)
        db.session.commit()
    return jsonify(toggle.to_dict()), 200

@admin_bp.route('/settings', methods=['POST'])
@require_role('admin')
def update_site_settings():
    from app.models import SiteFeatureToggle
    data = request.get_json() or {}
    toggle = SiteFeatureToggle.query.first()
    if not toggle:
        toggle = SiteFeatureToggle()
        db.session.add(toggle)

    if 'general_chat_enabled' in data:
        toggle.general_chat_enabled = bool(data['general_chat_enabled'])
    if 'allowed_email_domains' in data:
        toggle.allowed_email_domains = str(data['allowed_email_domains']).strip()
    if 'password_min_length' in data:
        toggle.password_min_length = int(data['password_min_length'])
    if 'announcement_enabled' in data:
        toggle.announcement_enabled = bool(data['announcement_enabled'])
    if 'announcement_banner' in data:
        toggle.announcement_banner = str(data['announcement_banner']).strip()

    toggle.updated_by_id = g.current_user.id
    db.session.commit()

    log_audit('SITE_SETTINGS_UPDATED', notes=f"Updated site settings. Announcement enabled: {toggle.announcement_enabled}, Banner: {toggle.announcement_banner}")
    return jsonify(toggle.to_dict()), 200



