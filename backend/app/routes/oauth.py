import secrets
import time
from flask import Blueprint, request, jsonify, redirect, url_for, g, render_template_string
from app.models import db, User, OAuth2Client, OAuth2AuthorizationCode, OAuth2Token
from app.utils.decorators import require_auth

oauth_bp = Blueprint('oauth', __name__, url_prefix='/oauth')

@oauth_bp.route('/authorize', methods=['GET', 'POST'])
@require_auth
def authorize():
    client_id = request.args.get('client_id') or request.form.get('client_id')
    redirect_uri = request.args.get('redirect_uri') or request.form.get('redirect_uri')
    response_type = request.args.get('response_type', 'code')
    state = request.args.get('state', '')

    client = OAuth2Client.query.filter_by(client_id=client_id).first()
    if not client:
        # Fallback if default CTFd client not registered yet
        client = OAuth2Client(
            client_id=client_id or 'ctfd-client-id-hx99',
            client_secret='ctfd-client-secret-sec88',
            client_name='CTFd Platform',
            redirect_uris=redirect_uri or 'http://ctf.hackerxploit.org/redirect',
            grant_types='authorization_code',
            response_types='code'
        )
        db.session.add(client)
        db.session.commit()

    if request.method == 'GET':
        # Simple consent auto-approve for logged in user on CTFd SSO
        code_val = secrets.token_hex(20)
        auth_code = OAuth2AuthorizationCode(
            code=code_val,
            client_id=client.client_id,
            redirect_uri=redirect_uri or client.get_default_redirect_uri(),
            user_id=g.current_user.id
        )
        db.session.add(auth_code)
        db.session.commit()

        target = f"{redirect_uri or client.get_default_redirect_uri()}?code={code_val}"
        if state:
            target += f"&state={state}"
        return redirect(target)

@oauth_bp.route('/token', methods=['POST'])
def token():
    grant_type = request.form.get('grant_type')
    code = request.form.get('code')
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    redirect_uri = request.form.get('redirect_uri')

    auth_code = OAuth2AuthorizationCode.query.filter_by(code=code).first()
    if not auth_code or auth_code.is_expired():
        return jsonify({'error': 'invalid_grant', 'error_description': 'Invalid or expired authorization code'}), 400

    access_token = secrets.token_hex(32)
    refresh_token = secrets.token_hex(32)

    tok = OAuth2Token(
        client_id=auth_code.client_id,
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=auth_code.user_id,
        expires_in=86400
    )
    db.session.add(tok)
    db.session.delete(auth_code)
    db.session.commit()

    return jsonify({
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': 86400,
        'refresh_token': refresh_token
    })

@oauth_bp.route('/userinfo', methods=['GET'])
def userinfo():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'invalid_token'}), 401
    
    token_str = auth_header.split(' ', 1)[1]
    tok = OAuth2Token.query.filter_by(access_token=token_str).first()
    if not tok or tok.is_expired():
        return jsonify({'error': 'invalid_token'}), 401

    user = User.query.get(tok.user_id)
    if not user:
        return jsonify({'error': 'user_not_found'}), 404

    return jsonify({
        'id': user.id,
        'name': user.full_name,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'avatar_url': user.avatar_url
    })
