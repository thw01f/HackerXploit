import os
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO

from app.config import Config
from app.models import db

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour"]
)

socketio = SocketIO(cors_allowed_origins="*")

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS with credentials for subdomains (.hackerxploit.org)
    CORS(app, supports_credentials=True, origins=[
        "http://hackerxploit.org",
        "http://club.hackerxploit.org",
        "http://ctf.hackerxploit.org",
        "http://localhost",
        "http://127.0.0.1"
    ])

    db.init_app(app)
    limiter.init_app(app)
    
    # Initialize SocketIO with redis message queue if available
    redis_url = app.config.get('REDIS_URL')
    socketio.init_app(app, message_queue=redis_url)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.oauth import oauth_bp
    from app.routes.uploads import uploads_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(uploads_bp)

    # Rate limiting on auth endpoints
    limiter.limit("5 per minute")(auth_bp)

    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'service': 'HackerXploit Auth & Core API'}, 200

    with app.app_context():
        # Ensure database tables exist
        db.create_all()

    return app
