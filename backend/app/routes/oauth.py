import secrets
import time
from urllib.parse import quote
from flask import Blueprint, request, jsonify, redirect, url_for, g, render_template_string, current_app
from app.models import db, User, OAuth2Client, OAuth2AuthorizationCode, OAuth2Token
from app.utils.decorators import get_current_user

oauth_bp = Blueprint('oauth', __name__, url_prefix='/oauth')

@oauth_bp.route('/authorize', methods=['GET', 'POST'])
def authorize():
    # Deliberately not @require_auth: unlike every other endpoint here, this
    # one is only ever reached by a full browser navigation (CTFd's "Login
    # with HackerXploit" button redirects the browser here directly) - a
    # user who isn't already logged in got a raw {"error": "Unauthorized..."}
    # JSON blob instead of a login page, which looked exactly like "SSO is
    # broken" to them even though their account was completely fine. Send
    # them to the actual login/setup/onboarding page instead, with a
    # `redirect` back to this exact URL so the OAuth flow resumes
    # automatically once they're done.
    user, _ = get_current_user()
    frontend_base = current_app.config.get('CTFD_OAUTH_PUBLIC_BASE_URL', 'https://club.hackerxploit.org')
    come_back_to = quote(request.full_path if request.query_string else request.path, safe='')

    if not user:
        return redirect(f'{frontend_base}/login?redirect={come_back_to}')
    if user.is_root_admin and user.is_first_login:
        return redirect(f'{frontend_base}/setup-admin?redirect={come_back_to}')
    if not user.is_root_admin and not bool(user.onboarding_completed):
        return redirect(f'{frontend_base}/onboarding?redirect={come_back_to}')

    g.current_user = user

    client_id = request.args.get('client_id') or request.form.get('client_id')
    redirect_uri = request.args.get('redirect_uri') or request.form.get('redirect_uri')
    response_type = request.args.get('response_type', 'code')
    state = request.args.get('state', '')

    client = OAuth2Client.query.filter_by(client_id=client_id).first()
    if not client:
        # One-time bootstrap for the pre-configured CTFd client only. Never derive
        # secret/redirect_uri from request input, and only when nothing is registered yet.
        configured_client_id = current_app.config.get('CTFD_OAUTH_CLIENT_ID')
        if client_id != configured_client_id:
            return jsonify({'error': 'invalid_client', 'error_description': 'Unknown client_id'}), 400

        client = OAuth2Client(
            client_id=configured_client_id,
            client_secret=current_app.config.get('CTFD_OAUTH_CLIENT_SECRET'),
            client_name='CTFd Platform',
            redirect_uris=current_app.config.get('CTFD_OAUTH_REDIRECT_URI', 'https://arena.hackerxploit.org/redirect'),
            grant_types='authorization_code',
            response_types='code'
        )
        db.session.add(client)
        db.session.commit()

    if not client.check_response_type(response_type):
        return jsonify({'error': 'unsupported_response_type'}), 400

    target_redirect_uri = redirect_uri or client.get_default_redirect_uri()
    if not client.check_redirect_uri(target_redirect_uri):
        return jsonify({'error': 'invalid_request', 'error_description': 'redirect_uri does not match a registered URI for this client'}), 400

    if request.method == 'GET':
        # Simple consent auto-approve for logged in user on CTFd SSO
        code_val = secrets.token_hex(20)
        auth_code = OAuth2AuthorizationCode(
            code=code_val,
            client_id=client.client_id,
            redirect_uri=target_redirect_uri,
            user_id=g.current_user.id
        )
        db.session.add(auth_code)
        db.session.commit()

        target = f"{target_redirect_uri}?code={code_val}"
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

    if grant_type != 'authorization_code':
        return jsonify({'error': 'unsupported_grant_type'}), 400

    if not client_id or not client_secret:
        return jsonify({'error': 'invalid_client', 'error_description': 'client_id and client_secret are required'}), 401

    client = OAuth2Client.query.filter_by(client_id=client_id).first()
    if not client or not client.check_client_secret(client_secret):
        return jsonify({'error': 'invalid_client', 'error_description': 'Client authentication failed'}), 401

    if not client.check_grant_type(grant_type):
        return jsonify({'error': 'unauthorized_client'}), 400

    auth_code = OAuth2AuthorizationCode.query.filter_by(code=code).first()
    if not auth_code or auth_code.is_expired():
        return jsonify({'error': 'invalid_grant', 'error_description': 'Invalid or expired authorization code'}), 400

    if auth_code.client_id != client.client_id:
        return jsonify({'error': 'invalid_grant', 'error_description': 'Authorization code was not issued to this client'}), 400

    # RFC 6749 4.1.3 says a client SHOULD send redirect_uri back here if one
    # was used at the authorize step, but CTFd's actual OAuth client (its
    # only consumer) never sends it at all - its token POST body is just
    # code/client_id/client_secret/grant_type. Requiring it unconditionally
    # meant every single token exchange 400'd here, for every user, always -
    # nobody could ever complete the SSO round-trip. Only validate it when
    # the client actually provided one; the code is already scoped to a
    # specific client_id and a server-stored redirect_uri, so a client that
    # omits this parameter (like CTFd) isn't gaining anything by omitting it.
    if redirect_uri and redirect_uri != auth_code.redirect_uri:
        return jsonify({'error': 'invalid_grant', 'error_description': 'redirect_uri does not match the authorization request'}), 400

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
