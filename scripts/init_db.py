import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app import create_app
from app.models import db, OAuth2Client

def seed_oauth_clients():
    app = create_app()
    with app.app_context():
        db.create_all()
        client = OAuth2Client.query.filter_by(client_id='ctfd-client-id-hx99').first()
        if not client:
            client = OAuth2Client(
                client_id='ctfd-client-id-hx99',
                client_secret='ctfd-client-secret-sec88',
                client_name='CTFd Official Platform',
                redirect_uris='http://ctf.hackerxploit.org/redirect http://localhost/redirect',
                grant_types='authorization_code',
                response_types='code',
                scope='profile email'
            )
            db.session.add(client)
            db.session.commit()
            print("Successfully registered CTFd OAuth2 SSO Client!")
        else:
            print("CTFd OAuth2 SSO Client already configured.")

if __name__ == '__main__':
    seed_oauth_clients()
