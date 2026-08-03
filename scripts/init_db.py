import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app import create_app
from app.models import db, User, OAuth2Client
from init_ctfd import init_ctfd_oauth

def seed_database():
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # 1. Seed Root Admin User
        root_user = User.query.filter_by(is_root_admin=True).first()
        if not root_user:
            root_user = User.query.filter_by(username='admin').first()
        
        if not root_user:
            root_user = User(
                username='admin',
                email='admin@hackerxploit.org',
                full_name='Root Administrator',
                role='admin',
                is_root_admin=True,
                status='approved',
                is_first_login=True
            )
            root_user.set_password('HackerXploit')
            db.session.add(root_user)
            db.session.commit()
            print("Successfully bootstrapped initial Root Admin (username: admin, password: HackerXploit, is_first_login: True)")
        else:
            print("Root Admin user already exists.")

        # 2. Seed CTFd OAuth2 Client
        # client_secret must come from the environment, not a hardcoded
        # placeholder - 'ctfd-client-secret-sec88' is the exact known-insecure
        # default backend/app/config.py's Config.CTFD_OAUTH_CLIENT_SECRET
        # fail-fast check rejects, so seeding the DB row with it here would
        # silently defeat that check: the app boots with a real secret, but
        # the actual stored OAuth2Client row (what the token endpoint
        # validates against) would still be the public placeholder value.
        client_id = os.getenv('CTFD_OAUTH_CLIENT_ID', 'ctfd-client-id-hx99')
        client_secret = os.getenv('CTFD_OAUTH_CLIENT_SECRET', 'ctfd-client-secret-sec88')
        client = OAuth2Client.query.filter_by(client_id=client_id).first()
        if not client:
            client = OAuth2Client(
                client_id=client_id,
                client_secret=client_secret,
                client_name='CTFd Official Platform',
                # https, not http - CTFd is served over TLS via nginx/Certbot
                # in production, and OAuth2Client.check_redirect_uri() does an
                # exact match, so a scheme mismatch here breaks the actual
                # "Login with HackerXploit" flow even though everything else
                # is configured correctly. http://localhost/redirect is kept
                # for local dev only.
                redirect_uris='https://arena.hackerxploit.org/redirect http://localhost/redirect https://arena.hackerxploit.org/oauth/redirect',
                grant_types='authorization_code',
                response_types='code',
                scope='profile email'
            )
            db.session.add(client)
            db.session.commit()
            print("Successfully registered CTFd OAuth2 SSO Client!")
        else:
            print("CTFd OAuth2 SSO Client already configured.")

        # 3. Seed CTFd Database OAuth Configuration
        init_ctfd_oauth()

if __name__ == '__main__':
    seed_database()
