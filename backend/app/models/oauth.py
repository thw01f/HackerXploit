import time
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class OAuth2Client(db.Model):
    __tablename__ = 'oauth2_clients'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(48), unique=True, nullable=False, index=True)
    client_secret = db.Column(db.String(120), nullable=False)
    client_name = db.Column(db.String(64), nullable=False)
    redirect_uris = db.Column(db.Text, nullable=False)  # Space-separated URLs
    grant_types = db.Column(db.Text, nullable=False)    # Space-separated grant types
    response_types = db.Column(db.Text, nullable=False) # Space-separated response types
    scope = db.Column(db.Text, default='profile email')

    def get_client_id(self):
        return self.client_id

    def get_default_redirect_uri(self):
        return self.redirect_uris.split()[0] if self.redirect_uris else None

    def check_redirect_uri(self, redirect_uri):
        return redirect_uri in self.redirect_uris.split()

    def check_client_secret(self, client_secret):
        return self.client_secret == client_secret

    def check_endpoint_auth_method(self, method, endpoint):
        return True

    def check_grant_type(self, grant_type):
        return grant_type in self.grant_types.split()

    def check_response_type(self, response_type):
        return response_type in self.response_types.split()

class OAuth2AuthorizationCode(db.Model):
    __tablename__ = 'oauth2_codes'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(120), unique=True, nullable=False, index=True)
    client_id = db.Column(db.String(48), nullable=False)
    redirect_uri = db.Column(db.Text, nullable=False)
    response_type = db.Column(db.Text, default='code')
    scope = db.Column(db.Text, default='profile email')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.Integer, default=lambda: int(time.time()))
    expires_in = db.Column(db.Integer, default=300)

    def is_expired(self):
        return int(time.time()) > self.created_at + self.expires_in

class OAuth2Token(db.Model):
    __tablename__ = 'oauth2_tokens'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(48), nullable=False)
    token_type = db.Column(db.String(40), default='Bearer')
    access_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    refresh_token = db.Column(db.String(255), unique=True, nullable=True, index=True)
    scope = db.Column(db.Text, default='profile email')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.Integer, default=lambda: int(time.time()))
    expires_in = db.Column(db.Integer, default=86400)

    def is_expired(self):
        return int(time.time()) > self.created_at + self.expires_in
