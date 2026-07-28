from functools import wraps
from flask import request, jsonify, g, session
from app.models import db, User, DeviceSession, AuditLog

def get_current_user():
    token = request.headers.get('Authorization')
    if token and token.startswith('Bearer '):
        token = token.split(' ', 1)[1]
    elif 'session_token' in session:
        token = session['session_token']
    else:
        token = request.cookies.get('session_token')

    if not token:
        return None, None

    device_session = DeviceSession.query.filter_by(session_token=token, is_active=True).first()
    if not device_session:
        return None, None

    user = User.query.get(device_session.user_id)
    if not user or user.status == 'suspended':
        # Immediate session kill-switch on suspension
        device_session.is_active = False
        db.session.commit()
        return None, None

    return user, device_session

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user, device_session = get_current_user()
        if not user:
            return jsonify({'error': 'Unauthorized or session invalidated'}), 401
        g.current_user = user
        g.current_session = device_session
        return f(*args, **kwargs)
    return decorated

def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user, device_session = get_current_user()
            if not user:
                return jsonify({'error': 'Unauthorized'}), 401
            
            # root_admin can do everything an admin or teacher can do
            user_roles = [user.role]
            if user.role == 'root_admin':
                user_roles.extend(['admin', 'teacher', 'member'])
            elif user.role == 'admin':
                user_roles.extend(['teacher', 'member'])
            elif user.role == 'teacher':
                user_roles.extend(['member'])

            if not any(r in roles for r in user_roles):
                return jsonify({'error': 'Forbidden: Insufficient privileges'}), 403

            g.current_user = user
            g.current_session = device_session
            return f(*args, **kwargs)
        return decorated
    return decorator

def require_root(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user, device_session = get_current_user()
        if not user or user.role != 'root_admin':
            return jsonify({'error': 'Forbidden: Root Admin access required'}), 403
        g.current_user = user
        g.current_session = device_session
        return f(*args, **kwargs)
    return decorated

def log_audit(action, target_type=None, target_id=None, details=None):
    user = getattr(g, 'current_user', None)
    actor_id = user.id if user else None
    actor_name = user.username if user else 'System'
    actor_role = user.role if user else 'system'
    ip_addr = request.remote_addr

    audit_entry = AuditLog(
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        action=action,
        target_type=target_type,
        target_id=str(target_id) if target_id else None,
        details=details or {},
        ip_address=ip_addr
    )
    db.session.add(audit_entry)
    db.session.commit()
