import secrets
import hashlib
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session, make_response, g, current_app
from app.models import db, User, DeviceSession, LoginAttempt, AuditLog, ProfileFieldDefinition, UserProfileValue, PasswordResetRequest, PasswordResetCode
from app.utils.captcha import verify_turnstile
from app.utils.decorators import require_auth, log_audit, get_current_user

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/custom-fields', methods=['GET'])
def get_public_custom_fields():
    fields = ProfileFieldDefinition.query.filter_by(active=True).order_by(ProfileFieldDefinition.id.asc()).all()
    return jsonify({'fields': [f.to_dict() for f in fields]}), 200

@auth_bp.route('/registration-config', methods=['GET'])
def get_registration_config():
    from app.models.moderation import SiteFeatureToggle
    toggle = SiteFeatureToggle.query.first()
    if not toggle:
        toggle = SiteFeatureToggle()
    return jsonify({
        'allowed_email_domains': toggle.allowed_email_domains or "gmail.com,srm.edu.in,hackerxploit.org",
        'min_password_length': toggle.password_min_length or 8,
        'general_chat_enabled': toggle.general_chat_enabled if toggle else True
    }), 200

@auth_bp.route('/public-settings', methods=['GET'])
def get_public_settings():
    from app.models.moderation import SiteFeatureToggle
    toggle = SiteFeatureToggle.query.first()
    if not toggle:
        toggle = SiteFeatureToggle()
    return jsonify({
        'general_chat_enabled': toggle.general_chat_enabled if toggle else True,
        'allowed_email_domains': toggle.allowed_email_domains or "",
        'min_password_length': toggle.password_min_length or 8
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    from app.models.moderation import SiteFeatureToggle
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    captcha_token = data.get('captcha_token', '')
    custom_field_values = data.get('custom_fields', {}) # dict of {field_key_or_id: value}

    if not verify_turnstile(captcha_token, request.remote_addr):
        return jsonify({'error': 'CAPTCHA verification failed'}), 400

    if not email or not username or not password:
        return jsonify({'error': 'Email, Username, and Password are required'}), 400

    # 1. Enforce Allowed Email Domains Restriction
    toggle = SiteFeatureToggle.query.first()
    if not toggle:
        toggle = SiteFeatureToggle()

    if toggle.allowed_email_domains and toggle.allowed_email_domains.strip() != '*':
        allowed_list = [d.strip().lower() for d in toggle.allowed_email_domains.split(',') if d.strip()]
        email_domain = email.split('@')[-1] if '@' in email else ''
        if allowed_list and email_domain not in allowed_list:
            return jsonify({
                'error': f'Registration is restricted to authorized email domains: {", ".join(["@" + d for d in allowed_list])}'
            }), 400

    # 2. Enforce CTFd-Aligned Password Length Restriction
    min_len = toggle.password_min_length or 8
    if len(password) < min_len:
        return jsonify({'error': f'Password must be at least {min_len} characters long'}), 400

    if User.query.filter((User.email == email) | (User.username == username)).first():
        return jsonify({'error': 'Email or Username already registered'}), 409

    # Determine if this is the first user ever (Root Admin creation)
    user_count = User.query.count()
    if user_count == 0:
        role = 'admin'
        is_root_admin = True
        status = 'approved'
        is_first_login = True
    else:
        role = 'member'
        is_root_admin = False
        status = 'pending'  # Needs admin/teacher approval
        is_first_login = False

    user = User(
        email=email,
        username=username,
        full_name=full_name or username,
        role=role,
        is_root_admin=is_root_admin,
        status=status,
        is_first_login=is_first_login,
        student_id=data.get('student_id'),
        graduation_year=data.get('graduation_year')
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # Process dynamic custom profile fields
    active_fields = ProfileFieldDefinition.query.filter_by(active=True).all()
    for field in active_fields:
        val = custom_field_values.get(field.field_key) or custom_field_values.get(str(field.id))
        if val is not None:
            pv = UserProfileValue(
                user_id=user.id,
                field_id=field.id,
                value=str(val)
            )
            db.session.add(pv)
    db.session.commit()

    log_audit(
        action='USER_REGISTER', 
        target_type='User', 
        target_id=user.id, 
        target_user_id=user.id,
        notes=f"User registered with status {status}"
    )

    return jsonify({
        'message': 'Registration successful' if status == 'approved' else 'Registration submitted for approval.',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/setup-admin', methods=['POST'])
@require_auth
def setup_admin():
    user = g.current_user
    if not user.is_first_login:
        return jsonify({'message': 'Initial setup already completed'}), 200

    data = request.get_json() or {}
    new_username = data.get('username', '').strip()
    new_email = data.get('email', '').strip().lower()
    new_password = data.get('password', '')

    if not new_username or not new_email or not new_password:
        return jsonify({'error': 'New username, email, and password are required'}), 400

    # Check collision if changed
    if new_username != user.username and User.query.filter_by(username=new_username).first():
        return jsonify({'error': 'Username already taken'}), 409
    if new_email != user.email and User.query.filter_by(email=new_email).first():
        return jsonify({'error': 'Email already registered'}), 409

    user.username = new_username
    user.email = new_email
    user.set_password(new_password)
    user.is_first_login = False
    db.session.commit()

    log_audit('setup_admin_complete', target_type='User', target_id=user.id, target_user_id=user.id, notes="Initial Root Admin setup completed")

    return jsonify({
        'message': 'Root admin credentials updated successfully',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    login_id = data.get('email_or_username', '').strip()
    password = data.get('password', '')

    user = User.query.filter(
        (User.email == login_id.lower()) | (User.username == login_id)
    ).first()

    ip_addr = request.remote_addr or '127.0.0.1'
    user_agent = request.user_agent.string if request.user_agent else 'Unknown'

    if not user:
        attempt = LoginAttempt(
            user_id=None,
            username_attempted=login_id,
            ip_address=ip_addr,
            user_agent=user_agent,
            success=False,
            failure_reason='User not found'
        )
        db.session.add(attempt)
        db.session.commit()
        return jsonify({'error': 'Invalid credentials'}), 401

    if user.is_locked():
        attempt = LoginAttempt(
            user_id=user.id,
            username_attempted=login_id,
            ip_address=ip_addr,
            user_agent=user_agent,
            success=False,
            failure_reason='Account locked due to consecutive failures'
        )
        db.session.add(attempt)
        db.session.commit()
        return jsonify({'error': 'Account is temporarily locked. Try again in 15 minutes.'}), 423

    # Validate password
    was_locked_before = user.is_locked()
    if not user.check_password(password):
        just_locked = user.is_locked()
        db.session.commit()
        
        attempt = LoginAttempt(
            user_id=user.id,
            username_attempted=login_id,
            ip_address=ip_addr,
            user_agent=user_agent,
            success=False,
            failure_reason=f'Incorrect password (attempt {user.failed_login_count}/5)'
        )
        db.session.add(attempt)
        
        if just_locked and not was_locked_before:
            audit = AuditLog(
                actor_id=user.id,
                actor_name=user.username,
                actor_role=user.role,
                target_user_id=user.id,
                action='auto_locked',
                notes=f'Account auto-locked after 5 consecutive failed login attempts from IP {ip_addr}',
                ip_address=ip_addr
            )
            db.session.add(audit)

        db.session.commit()
        return jsonify({'error': 'Invalid credentials'}), 401

    if user.status != 'approved':
        reason = f'Account status is {user.status}'
        attempt = LoginAttempt(
            user_id=user.id,
            username_attempted=login_id,
            ip_address=ip_addr,
            user_agent=user_agent,
            success=False,
            failure_reason=reason
        )
        db.session.add(attempt)
        db.session.commit()
        return jsonify({'error': f'Account cannot login: {reason}'}), 403

    # Success
    user.last_login_at = datetime.utcnow()
    user.failed_login_count = 0
    user.locked_until = None
    
    attempt = LoginAttempt(
        user_id=user.id,
        username_attempted=login_id,
        ip_address=ip_addr,
        user_agent=user_agent,
        success=True
    )
    db.session.add(attempt)

    # Create device session
    token = secrets.token_hex(32)
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    device_label = request.headers.get('User-Agent', 'Web Browser')[:100]

    device = DeviceSession(
        user_id=user.id,
        session_token=token,
        session_token_hash=token_hash,
        ip_address=ip_addr,
        user_agent=user_agent[:250],
        device_label=device_label,
        is_active=True
    )
    db.session.add(device)
    db.session.commit()

    resp = make_response(jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'require_setup': user.is_first_login
    }))

    cookie_domain = current_app.config.get('SESSION_COOKIE_DOMAIN', '.hackerxploit.org')
    resp.set_cookie(
        'session_token',
        token,
        domain=cookie_domain,
        httponly=True,
        secure=current_app.config.get('SESSION_COOKIE_SECURE', True),
        samesite=current_app.config.get('SESSION_COOKIE_SAMESITE', 'Lax'),
        max_age=86400 * 7
    )
    return resp, 200

@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    g.current_session.is_active = False
    db.session.commit()

    resp = make_response(jsonify({'message': 'Logged out successfully'}))
    cookie_domain = current_app.config.get('SESSION_COOKIE_DOMAIN', '.hackerxploit.org')
    resp.delete_cookie('session_token', domain=cookie_domain)
    return resp, 200

@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_me():
    return jsonify({'user': g.current_user.to_dict()}), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
    login_id = data.get('email_or_username', '').strip()
    captcha_token = data.get('captcha_token', '')

    if not verify_turnstile(captcha_token, request.remote_addr):
        return jsonify({'error': 'CAPTCHA verification failed'}), 400

    user = User.query.filter(
        (User.email == login_id.lower()) | (User.username == login_id)
    ).first()

    if not user:
        # Return generic success to avoid enumeration
        return jsonify({'message': 'If account exists, password reset request has been logged for admin review.'}), 200

    req = PasswordResetRequest(user_id=user.id, status='pending')
    db.session.add(req)
    db.session.commit()

    log_audit('PASSWORD_RESET_REQUESTED', target_type='User', target_id=user.id, target_user_id=user.id, notes="User submitted password reset request")

    return jsonify({'message': 'Password reset request submitted to admin queue.'}), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    code_str = data.get('code', '').strip().upper()
    new_password = data.get('password', '')

    if not code_str or not new_password:
        return jsonify({'error': 'Code and new password are required'}), 400

    reset_code = PasswordResetCode.query.filter_by(code=code_str).first()
    if not reset_code or not reset_code.is_valid():
        return jsonify({'error': 'Invalid or expired reset code'}), 400

    user = User.query.get(reset_code.user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.set_password(new_password)
    user.failed_login_count = 0
    user.locked_until = None
    reset_code.used_at = datetime.utcnow()

    # Mark pending requests fulfilled
    reqs = PasswordResetRequest.query.filter_by(user_id=user.id, status='pending').all()
    for r in reqs:
        r.status = 'fulfilled'

    db.session.commit()

    log_audit('PASSWORD_RESET_COMPLETED', target_type='User', target_id=user.id, target_user_id=user.id, notes="Password reset using admin-issued code")

    return jsonify({'message': 'Password reset successfully. You may now log in.'}), 200

@auth_bp.route('/onboarding', methods=['POST'])
@require_auth
def complete_onboarding():
    data = request.get_json() or {}
    user = g.current_user
    
    spec_role = data.get('specialization_role', '').strip()
    if spec_role in ['Security Analyst', 'Penetration Tester', 'Security Engineer']:
        user.specialization_role = spec_role

    if data.get('full_name'):
        user.full_name = data.get('full_name').strip()
    if data.get('student_id'):
        user.student_id = data.get('student_id').strip()
    if data.get('academic_year'):
        user.academic_year = data.get('academic_year').strip()
    if data.get('department'):
        user.department = data.get('department').strip()
    if data.get('graduation_year'):
        try:
            user.graduation_year = int(data.get('graduation_year'))
        except (ValueError, TypeError):
            pass
    if data.get('bio'):
        user.bio = data.get('bio').strip()

    if 'gmail' in data: user.gmail = (data.get('gmail') or '').strip()
    if 'personal_gmail' in data: user.personal_gmail = (data.get('personal_gmail') or '').strip()
    if 'student_gmail' in data: user.student_gmail = (data.get('student_gmail') or '').strip()
    if 'phone_number' in data: user.phone_number = (data.get('phone_number') or '').strip()

    if 'website_url' in data: user.website_url = (data.get('website_url') or '').strip()
    if 'github_url' in data: user.github_url = (data.get('github_url') or '').strip()
    if 'linkedin_url' in data: user.linkedin_url = (data.get('linkedin_url') or '').strip()
    if 'tryhackme_url' in data: user.tryhackme_url = (data.get('tryhackme_url') or '').strip()
    if 'htb_url' in data: user.htb_url = (data.get('htb_url') or '').strip()
    if 'resume_url' in data: user.resume_url = (data.get('resume_url') or '').strip()

    # Process custom profile fields
    custom_fields = data.get('custom_fields') or {}
    if isinstance(custom_fields, dict):
        from app.models.user import UserProfileValue, ProfileFieldDefinition
        for field_key, value in custom_fields.items():
            field_def = ProfileFieldDefinition.query.filter_by(field_key=field_key, active=True).first()
            if field_def:
                pval = UserProfileValue.query.filter_by(user_id=user.id, field_id=field_def.id).first()
                if not pval:
                    pval = UserProfileValue(user_id=user.id, field_id=field_def.id)
                    db.session.add(pval)
                pval.value = str(value)

    user.is_first_login = False
    user.onboarding_completed = True
    db.session.commit()

    # Sync user details to CTFd container
    try:
        from app.services.ctfd_sync import sync_user_to_ctfd
        sync_user_to_ctfd(user)
    except Exception as e:
        print(f"CTFd onboarding sync note: {e}")

    log_audit('ONBOARDING_COMPLETED', target_type='User', target_id=user.id, target_user_id=user.id, notes=f"Completed onboarding with specialization: {user.specialization_role}")
    return jsonify({'message': 'Onboarding profile saved successfully', 'user': user.to_dict(include_private=True)}), 200
