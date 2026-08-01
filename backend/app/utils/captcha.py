import os
import requests
from flask import current_app

def verify_turnstile(token, remote_ip=None):
    secret = current_app.config.get('TURNSTILE_SECRET_KEY')
    is_production = os.environ.get('FLASK_ENV', 'production') == 'production'

    # Dev-only bypass: never honored in production, regardless of token/secret supplied.
    if not is_production and (not secret or token == 'DEV_BYPASS_TOKEN' or secret.startswith('1x000000')):
        return True

    if not secret:
        return False

    url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
    payload = {
        'secret': secret,
        'response': token
    }
    if remote_ip:
        payload['remoteip'] = remote_ip

    try:
        res = requests.post(url, data=payload, timeout=5)
        data = res.json()
        return data.get('success', False)
    except Exception:
        # Fail closed: an unreachable verification API must not grant a bypass.
        return False
