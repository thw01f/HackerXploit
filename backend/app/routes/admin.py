import secrets
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g
from app.models import db, User, DeviceSession, LoginAttempt, AuditLog, PasswordResetRequest, PasswordResetCode, ProfileFieldDefinition
from app.utils.decorators import require_auth, require_role, require_root, log_audit

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# -------------------------------------------------------------------
# 1. Approval Workflow (/admin/users) - Admin & Teacher allowed
# -------------------------------------------------------------------
@admin_bp.route('/users', methods=['GET'])
@require_role('teacher', 'admin')
def list_users():
    status = request.args.get('status')
    query = User.query
    if status:
        query = query.filter_by(status=status)
    users = query.order_by(User.created_at.desc()).all()
    return jsonify({'users': [u.to_dict() for u in users]}), 200

@admin_bp.route('/users/<int:user_id>/approve', methods=['POST'])
@require_role('teacher', 'admin')
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'approved'
    user.approved_by = g.current_user.id
    user.approved_at = datetime.utcnow()
    db.session.commit()

    log_audit('approved', target_type='User', target_id=user_id, target_user_id=user_id, notes=f"Approved by {g.current_user.username}")
    return jsonify(user.to_dict()), 200

@admin_bp.route('/users/<int:user_id>/reject', methods=['POST'])
@require_role('teacher', 'admin')
def reject_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_root_admin:
        return jsonify({'error': 'Root admin cannot be rejected'}), 403

    user.status = 'rejected'
    db.session.commit()

    log_audit('rejected', target_type='User', target_id=user_id, target_user_id=user_id, notes=f"Rejected by {g.current_user.username}")
    return jsonify(user.to_dict()), 200

@admin_bp.route('/users/<int:user_id>/suspend', methods=['POST'])
@require_role('teacher', 'admin')
def suspend_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_root_admin:
        return jsonify({'error': 'Root Admin cannot be suspended'}), 403

    user.status = 'suspended'
    
    # KILL-SWITCH: Invalidate all live device sessions immediately
    DeviceSession.query.filter_by(user_id=user_id, is_active=True).update({'is_active': False})
    db.session.commit()

    log_audit('suspended', target_type='User', target_id=user_id, target_user_id=user_id, notes=f"Suspended by {g.current_user.username}")
    return jsonify(user.to_dict()), 200

@admin_bp.route('/users/<int:user_id>/reinstate', methods=['POST'])
@require_role('teacher', 'admin')
def reinstate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'approved'
    db.session.commit()

    log_audit('reinstated', target_type='User', target_id=user_id, target_user_id=user_id, notes=f"Reinstated by {g.current_user.username}")
    return jsonify(user.to_dict()), 200

# -------------------------------------------------------------------
# 2. Site-wide Audit Log (/admin/audit-log) - Admin only
# -------------------------------------------------------------------
@admin_bp.route('/audit-log', methods=['GET'])
@require_role('admin')
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
    return jsonify({'message': f'User {user.username} unlocked successfully', 'user': user.to_dict()}), 200

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
    expires_at = datetime.utcnow() + timedelta(minutes=30)

    reset_code = PasswordResetCode(
        user_id=user.id,
        code=code,
        issued_by_admin_id=g.current_user.id,
        expires_at=expires_at
    )
    db.session.add(reset_code)
    db.session.commit()

    log_audit('PASSWORD_RESET_CODE_ISSUED', target_type='User', target_id=user.id, target_user_id=user.id, notes=f"Issued code {code} expiring in 30m")

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
        required=required,
        active=True,
        created_by=g.current_user.id
    )
    db.session.add(pf)
    db.session.commit()

    log_audit('PROFILE_FIELD_CREATED', target_type='ProfileFieldDefinition', target_id=pf.id, notes=f"Created custom profile field {field_key}")
    return jsonify(pf.to_dict()), 201

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
    if 'required' in data:
        pf.required = bool(data['required'])
    if 'active' in data:
        pf.active = bool(data['active'])

    db.session.commit()
    log_audit('PROFILE_FIELD_UPDATED', target_type='ProfileFieldDefinition', target_id=field_id, notes=f"Updated profile field {pf.field_key}")
    return jsonify(pf.to_dict()), 200

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
