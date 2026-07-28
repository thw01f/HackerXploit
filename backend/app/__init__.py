import os
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO

from app.config import Config
from app.models import db

# Initialize Sentry Error Tracking if DSN configured
sentry_dsn = os.getenv('SENTRY_DSN')
if sentry_dsn:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration

        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FlaskIntegration(), CeleryIntegration()],
            traces_sample_rate=0.2,
            environment=os.getenv('FLASK_ENV', 'production')
        )
    except Exception as e:
        print(f"Sentry SDK initialization warning: {e}")

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour"]
)

socketio = SocketIO(cors_allowed_origins="*")

def create_app(config_class=Config):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)

    # Enable CORS with credentials for subdomains (.hackerxploit.org)
    CORS(flask_app, supports_credentials=True, origins=[
        "http://hackerxploit.org",
        "http://club.hackerxploit.org",
        "http://ctf.hackerxploit.org",
        "http://localhost",
        "http://127.0.0.1"
    ])

    db.init_app(flask_app)
    limiter.init_app(flask_app)
    
    # Initialize SocketIO with redis message queue if available
    redis_url = flask_app.config.get('REDIS_URL')
    socketio.init_app(flask_app, message_queue=redis_url)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.oauth import oauth_bp
    from app.routes.uploads import uploads_bp
    from app.routes.chat import chat_bp
    from app.routes.admin import admin_bp
    from app.routes.club import club_bp
    from app.routes.academy import academy_bp
    from app.routes.competition import competition_bp
    from app.routes.opportunity import opportunity_bp
    from app.routes.search import search_bp
    from app.routes.activity import activity_bp
    from app.routes.students import students_bp
    from app.routes.leaderboard import leaderboard_bp
    from app.routes.notifications import notifications_bp
    from app.routes.inbox import inbox_bp
    from app.routes.reports import reports_bp

    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(oauth_bp)
    flask_app.register_blueprint(uploads_bp)
    flask_app.register_blueprint(chat_bp)
    flask_app.register_blueprint(admin_bp)
    flask_app.register_blueprint(club_bp)
    flask_app.register_blueprint(academy_bp)
    flask_app.register_blueprint(competition_bp)
    flask_app.register_blueprint(opportunity_bp)
    flask_app.register_blueprint(search_bp)
    flask_app.register_blueprint(activity_bp)
    flask_app.register_blueprint(students_bp)
    flask_app.register_blueprint(leaderboard_bp)
    flask_app.register_blueprint(notifications_bp)
    flask_app.register_blueprint(inbox_bp)
    flask_app.register_blueprint(reports_bp)



    import app.services.socket_events

    # Rate limiting on auth endpoints
    limiter.limit("5 per minute")(auth_bp)

    @flask_app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'service': 'HackerXploit Auth & Core API'}, 200

    with flask_app.app_context():
        # Ensure database tables exist
        db.create_all()

    return flask_app
