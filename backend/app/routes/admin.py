from flask import Blueprint, request, jsonify, g
from app.models import db, User, DeviceSession, LoginActivity, AuditLog
from app.utils.decorators import require_auth, require_role, require_root, log_audit

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/users', methods=['GET'])
@require_role('teacher', 'admin', 'root_admin')
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({'users': [u.to_dict() for u in users]}), 200

@admin_bp.route('/users/<int:user_id>/approve', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'approved'
    db.session.commit()
    log_audit('USER_APPROVE', target_type='User', target_id=user_id)
    return jsonify(user.to_dict()), 200

@admin_bp.route('/users/<int:user_id>/suspend', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def suspend_user(user_id):
    user = User.query.get_or_404(user_id)

    # Protect root_admin
    if user.role == 'root_admin':
        return jsonify({'error': 'Root Admin cannot be suspended'}), 403

    user.status = 'suspended'
    
    # KILL-SWITCH: Invalidate all live device sessions immediately
    DeviceSession.query.filter_by(user_id=user_id, is_active=True).update({'is_active': False})
    db.session.commit()

    log_audit('USER_SUSPEND', target_type='User', target_id=user_id)
    return jsonify(user.to_dict()), 200

@admin_bp.route('/users/<int:user_id>/role', methods=['POST'])
@require_root
def change_user_role(user_id):
    data = request.get_json() or {}
    new_role = data.get('role')

    allowed_roles = {'admin', 'teacher', 'member'}
    if new_role not in allowed_roles:
        return jsonify({'error': 'Invalid role specified'}), 400

    user = User.query.get_or_404(user_id)
    if user.role == 'root_admin':
        return jsonify({'error': 'Cannot change Root Admin role directly. Use transfer root.'}), 403

    # Enforce Hard Cap of 5 Admins
    if new_role == 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count >= 5:
            return jsonify({'error': 'Admin limit reached: Maximum 5 concurrent admins permitted'}), 400

    user.role = new_role
    db.session.commit()

    log_audit('USER_ROLE_CHANGE', target_type='User', target_id=user_id, details={'new_role': new_role})
    return jsonify(user.to_dict()), 200

@admin_bp.route('/transfer-root', methods=['POST'])
@require_root
def transfer_root():
    data = request.get_json() or {}
    target_user_id = data.get('target_user_id')

    target_user = User.query.get_or_404(target_user_id)
    current_root = g.current_user

    current_root.role = 'admin'
    target_user.role = 'root_admin'
    target_user.status = 'approved'
    db.session.commit()

    log_audit('TRANSFER_ROOT_STATUS', target_type='User', target_id=target_user_id)
    return jsonify({'message': f'Root admin status transferred to {target_user.username}'}), 200

@admin_bp.route('/security/login-activity', methods=['GET'])
@require_role('admin', 'root_admin')  # Strictly Admin/Root only (Teachers prohibited)
def get_login_activity():
    activities = LoginActivity.query.order_by(LoginActivity.timestamp.desc()).limit(100).all()
    return jsonify({'activities': [a.to_dict() for a in activities]}), 200

@admin_bp.route('/audit-logs', methods=['GET'])
@require_role('teacher', 'admin', 'root_admin')
def get_audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return jsonify({'audit_logs': [l.to_dict() for l in logs]}), 200
