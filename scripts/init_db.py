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
        client = OAuth2Client.query.filter_by(client_id='ctfd-client-id-hx99').first()
        if not client:
            client = OAuth2Client(
                client_id='ctfd-client-id-hx99',
                client_secret='ctfd-client-secret-sec88',
                client_name='CTFd Official Platform',
                redirect_uris='http://arena.hackerxploit.org/redirect http://localhost/redirect http://arena.hackerxploit.org/oauth/redirect',
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
