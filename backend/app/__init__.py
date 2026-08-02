import os
import shutil
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

    # Enable CORS with credentials for subdomains (.hackerxploit.org) & local ports
    CORS(flask_app, supports_credentials=True, origins=[
        "http://hackerxploit.org",
        "http://club.hackerxploit.org",
        "http://arena.hackerxploit.org",
        "http://localhost",
        "http://127.0.0.1",
        r"http://localhost:.*",
        r"http://127.0.0.1:.*"
    ])


    db.init_app(flask_app)
    limiter.init_app(flask_app)
    
    # Initialize SocketIO — only attach Redis message_queue in production
    # (Redis SocketIO requires gevent monkey-patching which conflicts with Werkzeug debug reloader)
    redis_url = flask_app.config.get('REDIS_URL')
    flask_env = os.getenv('FLASK_ENV', 'production')
    if redis_url and flask_env == 'production':
        socketio.init_app(flask_app, message_queue=redis_url)
    else:
        socketio.init_app(flask_app)


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
    from app.routes.portfolio import portfolio_bp
    from app.routes.privacy import privacy_bp
    from app.routes.backups import backups_bp
    from app.routes.id_card import id_card_bp
    from app.routes.support import support_bp
    from app.routes.roadmap import roadmap_bp
    from app.routes.announcement import announcement_bp

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
    flask_app.register_blueprint(portfolio_bp)
    flask_app.register_blueprint(privacy_bp)
    flask_app.register_blueprint(backups_bp)
    flask_app.register_blueprint(id_card_bp)
    flask_app.register_blueprint(support_bp)
    flask_app.register_blueprint(roadmap_bp)
    flask_app.register_blueprint(announcement_bp)



    import app.services.socket_events

    # Rate limiting on auth endpoints
    limiter.limit("5 per minute")(auth_bp)

    @flask_app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'service': 'HackerXploit Auth & Core API'}, 200

    with flask_app.app_context():
        # Ensure database tables exist
        db.create_all()
        from sqlalchemy import text
        for stmt in [
            "ALTER TABLE profile_field_definitions ADD COLUMN target_role VARCHAR(32) DEFAULT 'all'",
            "ALTER TABLE site_feature_toggles ADD COLUMN allowed_email_domains VARCHAR(512) DEFAULT 'gmail.com,srm.edu.in,hackerxploit.org'",
            "ALTER TABLE site_feature_toggles ADD COLUMN password_min_length INTEGER DEFAULT 8",
            "ALTER TABLE site_feature_toggles ADD COLUMN password_require_uppercase BOOLEAN DEFAULT TRUE",
            "ALTER TABLE site_feature_toggles ADD COLUMN password_require_lowercase BOOLEAN DEFAULT TRUE",
            "ALTER TABLE site_feature_toggles ADD COLUMN password_require_number BOOLEAN DEFAULT TRUE",
            "ALTER TABLE site_feature_toggles ADD COLUMN password_require_special BOOLEAN DEFAULT TRUE",
            "ALTER TABLE site_feature_toggles ADD COLUMN announcement_banner VARCHAR(512)",
            "ALTER TABLE users ADD COLUMN personal_gmail VARCHAR(255)",
            "ALTER TABLE users ADD COLUMN student_gmail VARCHAR(255)",
            "ALTER TABLE users ADD COLUMN resume_url VARCHAR(255)",
            "ALTER TABLE users ADD COLUMN badge_id VARCHAR(64)",
            "ALTER TABLE competition_participation ADD COLUMN application_screenshots JSON DEFAULT '[]'",
            "ALTER TABLE competition_participation ADD COLUMN github_link VARCHAR(512)",
            "ALTER TABLE competition_participation ADD COLUMN prize_money VARCHAR(128)",
            "ALTER TABLE competition_participation ADD COLUMN user_certificate_file VARCHAR(256)",
            "ALTER TABLE competition_participation ADD COLUMN self_reported_result VARCHAR(32)",
            "ALTER TABLE competition_participation ADD COLUMN completion_status VARCHAR(32) DEFAULT 'not_submitted'",
            "ALTER TABLE competition_participation ADD COLUMN completion_submitted_at TIMESTAMP",
            "UPDATE competition_participation SET application_screenshots = to_json(ARRAY[application_screenshot]) WHERE application_screenshot IS NOT NULL AND (application_screenshots IS NULL OR application_screenshots::text = '[]')"
        ]:
            try:
                db.session.execute(text(stmt))
                db.session.commit()
            except Exception:
                db.session.rollback()

        # One-time backfill: migrate the old single-string dashboard banner into
        # the new multi-announcement table, preserving the previously-hardcoded
        # "LAUNCH CTF ARENA" CTA so existing deployments don't lose it silently.
        try:
            from app.models import Announcement
            from app.models.moderation import SiteFeatureToggle
            if Announcement.query.count() == 0:
                toggle = SiteFeatureToggle.query.first()
                if toggle and toggle.announcement_enabled and (toggle.announcement_banner or '').strip():
                    db.session.add(Announcement(
                        message=toggle.announcement_banner.strip(),
                        button_label='LAUNCH CTF ARENA',
                        link='https://arena.hackerxploit.org',
                        is_active=True,
                        display_order=0
                    ))
                    db.session.commit()
        except Exception:
            db.session.rollback()

        # Every avatar_url fallback across the app (and the users.avatar_url
        # column default) points at /uploads/avatars/default.png, but that
        # path lives on the uploads_data volume, which starts out empty on a
        # fresh install or after a volume recreation - so it 404s until
        # something actually puts a file there. Self-heal it here rather than
        # relying on a manual step, from the bundled asset shipped in the repo.
        try:
            bundled_default_avatar = os.path.join(
                os.path.dirname(__file__), 'static', 'defaults', 'default_avatar.png'
            )
            avatars_dir = os.path.join(flask_app.config['UPLOAD_FOLDER'], 'avatars')
            live_default_avatar = os.path.join(avatars_dir, 'default.png')
            if os.path.exists(bundled_default_avatar) and not os.path.exists(live_default_avatar):
                os.makedirs(avatars_dir, exist_ok=True)
                shutil.copyfile(bundled_default_avatar, live_default_avatar)
        except Exception:
            pass

    return flask_app
