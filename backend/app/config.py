import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-default-key-hx99')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://hx_user:hx_secure_password_123!@db:5432/hackerxploit')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
    
    SESSION_COOKIE_DOMAIN = os.environ.get('SESSION_COOKIE_DOMAIN', '.hackerxploit.org')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/var/uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max file upload
    
    TURNSTILE_SECRET_KEY = os.environ.get('TURNSTILE_SECRET_KEY', '1x0000000000000000000000000000000AA')
    TURNSTILE_SITE_KEY = os.environ.get('TURNSTILE_SITE_KEY', '1x00000000000000000000AA')
    
    CTFD_OAUTH_CLIENT_ID = os.environ.get('CTFD_OAUTH_CLIENT_ID', 'ctfd-client-id-hx99')
    CTFD_OAUTH_CLIENT_SECRET = os.environ.get('CTFD_OAUTH_CLIENT_SECRET', 'ctfd-client-secret-sec88')
