import secrets
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session, make_response, g, current_app
from app.models import db, User, DeviceSession, LoginActivity
from app.utils.captcha import verify_turnstile
from app.utils.decorators import require_auth, log_audit

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    captcha_token = data.get('captcha_token', '')

    if not verify_turnstile(captcha_token, request.remote_addr):
        return jsonify({'error': 'CAPTCHA verification failed'}), 400

    if not email or not username or not password or not full_name:
        return jsonify({'error': 'All fields are required'}), 400

    if User.query.filter((User.email == email) | (User.username == username)).first():
        return jsonify({'error': 'Email or Username already registered'}), 409

    # Determine if this is the first user ever (Root Admin creation)
    user_count = User.query.count()
    if user_count == 0:
        role = 'root_admin'
        status = 'approved'
    else:
        role = 'member'
        status = 'pending'  # Needs admin/teacher approval

    user = User(
        email=email,
        username=username,
        full_name=full_name,
        role=role,
        status=status,
        student_id=data.get('student_id'),
        graduation_year=data.get('graduation_year')
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    log_audit('USER_REGISTER', target_type='User', target_id=user.id, details={'email': email, 'role': role})

    return jsonify({
        'message': 'Registration successful' if status == 'approved' else 'Registration submitted for approval.',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    login_id = data.get('email_or_username', '').strip()
    password = data.get('password', '')

    user = User.query.filter(
        (User.email == login_id.lower()) | (User.username == login_id)
    ).first()

    ip_addr = request.remote_addr
    user_agent = request.user_agent.string

    if not user:
        activity = LoginActivity(
            user_id=None,
            email_attempted=login_id,
            ip_address=ip_addr,
            user_agent=user_agent,
            success=False,
            failure_reason='User not found'
        )
        db.session.add(activity)
        db.session.commit()
        return jsonify({'error': 'Invalid credentials'}), 401

    if user.is_locked():
        activity = LoginActivity(
            user_id=user.id,
            email_attempted=login_id,
            ip_address=ip_addr,
            user_agent=user_agent,
            success=False,
            failure_reason='Account locked due to consecutive failures'
        )
        db.session.add(activity)
        db.session.commit()
        return jsonify({'error': 'Account is temporarily locked. Try again in 15 minutes.'}), 423

    if not user.check_password(password):
        db.session.commit()
        activity = LoginActivity(
            user_id=user.id,
            email_attempted=login_id,
            ip_address=ip_addr,
            user_agent=user_agent,
            success=False,
            failure_reason=f'Incorrect password (attempt {user.failed_login_attempts}/5)'
        )
        db.session.add(activity)
        db.session.commit()
        return jsonify({'error': 'Invalid credentials'}), 401

    if user.status != 'approved':
        reason = f'Account status is {user.status}'
        activity = LoginActivity(
            user_id=user.id,
            email_attempted=login_id,
            ip_address=ip_addr,
            user_agent=user_agent,
            success=False,
            failure_reason=reason
        )
        db.session.add(activity)
        db.session.commit()
        return jsonify({'error': f'Account cannot login: {reason}'}), 403

    # Success
    activity = LoginActivity(
        user_id=user.id,
        email_attempted=login_id,
        ip_address=ip_addr,
        user_agent=user_agent,
        success=True
    )
    db.session.add(activity)

    # Create session token
    token = secrets.token_hex(32)
    device = DeviceSession(
        user_id=user.id,
        session_token=token,
        ip_address=ip_addr,
        user_agent=user_agent[:250],
        device_name=request.headers.get('User-Agent', 'Web Browser')[:100],
        is_active=True
    )
    db.session.add(device)
    db.session.commit()

    resp = make_response(jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    }))

    cookie_domain = current_app.config.get('SESSION_COOKIE_DOMAIN', '.hackerxploit.org')
    resp.set_cookie(
        'session_token',
        token,
        domain=cookie_domain,
        httponly=True,
        samesite='Lax',
        max_age=86400 * 7
    )
    return resp, 200

@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    session_token = g.current_session.session_token
    device = DeviceSession.query.filter_by(session_token=session_token).first()
    if device:
        device.is_active = False
        db.session.commit()

    resp = make_response(jsonify({'message': 'Logged out successfully'}))
    cookie_domain = current_app.config.get('SESSION_COOKIE_DOMAIN', '.hackerxploit.org')
    resp.delete_cookie('session_token', domain=cookie_domain)
    return resp, 200

@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_me():
    return jsonify({'user': g.current_user.to_dict()}), 200

@auth_bp.route('/sessions', methods=['GET'])
@require_auth
def get_user_sessions():
    sessions = DeviceSession.query.filter_by(user_id=g.current_user.id, is_active=True).all()
    return jsonify({'sessions': [s.to_dict() for s in sessions]}), 200

@auth_bp.route('/sessions/<int:session_id>/revoke', methods=['POST'])
@require_auth
def revoke_session(session_id):
    device = DeviceSession.query.filter_by(id=session_id, user_id=g.current_user.id).first()
    if not device:
        return jsonify({'error': 'Session not found'}), 404
    device.is_active = False
    db.session.commit()
    log_audit('SESSION_REVOKE', target_type='DeviceSession', target_id=session_id)
    return jsonify({'message': 'Session revoked successfully'}), 200
