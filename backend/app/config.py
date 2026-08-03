import os

IS_PRODUCTION = os.environ.get('FLASK_ENV', 'production') == 'production'

# Values that must never be used in production - they're published in this
# repo's docker-compose.yml/.env.example as local-dev-only placeholders.
_INSECURE_DEFAULTS = {
    'SECRET_KEY': {'super-secret-default-key-hx99', 'super-secret-production-key-change-me-in-prod', ''},
    'POSTGRES_PASSWORD_IN_DATABASE_URL': {'hx_secure_password_123!'},
    'CTFD_OAUTH_CLIENT_SECRET': {'ctfd-client-secret-sec88', ''},
    # Cloudflare's publicly documented "always passes" Turnstile test secret -
    # legitimate for local dev, but if this ships to production unnoticed the
    # CAPTCHA on register/login/forgot-password accepts every attempt.
    'TURNSTILE_SECRET_KEY': {'1x0000000000000000000000000000000AA', ''},
}


def _require_secret(name, value, insecure_values):
    if IS_PRODUCTION and (not value or value in insecure_values):
        raise RuntimeError(
            f"Refusing to start in production: {name} is unset or is a known insecure "
            f"placeholder value. Set a unique secret via the environment."
        )
    return value


def _database_uri_has_insecure_password(uri):
    # A generator expression inside a class body can't see the class body's
    # own local variables (only closures/globals) - calling this as a plain
    # function from the class body sidesteps that scoping gotcha, since the
    # argument is evaluated in the class body's own scope before the call.
    return any(bad in uri for bad in _INSECURE_DEFAULTS['POSTGRES_PASSWORD_IN_DATABASE_URL'])


class Config:
    SECRET_KEY = _require_secret(
        'SECRET_KEY',
        os.environ.get('SECRET_KEY', ''),
        _INSECURE_DEFAULTS['SECRET_KEY'],
    ) or 'dev-only-insecure-key'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://hx_user:hx_secure_password_123!@db:5432/hackerxploit')
    if IS_PRODUCTION and _database_uri_has_insecure_password(SQLALCHEMY_DATABASE_URI):
        raise RuntimeError(
            "Refusing to start in production: DATABASE_URL contains the known insecure "
            "placeholder Postgres password. Set a unique password via the environment."
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')

    # Scoped to club. only (not the wildcard .hackerxploit.org) - the bare
    # root domain is reserved for other, unrelated projects as of
    # 2026-08-03, and this cookie has no reason to be sent to them.
    SESSION_COOKIE_DOMAIN = os.environ.get('SESSION_COOKIE_DOMAIN', '.club.hackerxploit.org')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'true' if IS_PRODUCTION else 'false').lower() == 'true'

    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/var/uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max file upload

    # Deliberately NOT under UPLOAD_FOLDER: nginx serves that tree publicly at /uploads/,
    # and database backup archives must never be reachable without authentication.
    BACKUP_FOLDER = os.environ.get('BACKUP_FOLDER', '/var/hx_backups')

    TURNSTILE_SECRET_KEY = _require_secret(
        'TURNSTILE_SECRET_KEY',
        os.environ.get('TURNSTILE_SECRET_KEY', ''),
        _INSECURE_DEFAULTS['TURNSTILE_SECRET_KEY'],
    ) or '1x0000000000000000000000000000000AA'
    TURNSTILE_SITE_KEY = os.environ.get('TURNSTILE_SITE_KEY', '1x00000000000000000000AA')

    CTFD_OAUTH_CLIENT_ID = os.environ.get('CTFD_OAUTH_CLIENT_ID', 'ctfd-client-id-hx99')
    CTFD_OAUTH_CLIENT_SECRET = _require_secret(
        'CTFD_OAUTH_CLIENT_SECRET',
        os.environ.get('CTFD_OAUTH_CLIENT_SECRET', ''),
        _INSECURE_DEFAULTS['CTFD_OAUTH_CLIENT_SECRET'],
    ) or 'dev-only-insecure-secret'
