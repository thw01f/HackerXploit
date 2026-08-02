from datetime import datetime
from app.models import db

class DeviceSession(db.Model):
    __tablename__ = 'device_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    session_token = db.Column(db.String(128), unique=True, nullable=False, index=True)
    session_token_hash = db.Column(db.String(128), nullable=True)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(255), nullable=False)
    device_label = db.Column(db.String(128), default='Unknown Device')
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        # Deliberately excludes session_token/session_token_hash: this is returned
        # to the session owner and to admins viewing device lists, and including
        # the live token would let either party hijack the session directly.
        # device_label duplicates user_agent (same raw header, just truncated
        # shorter) and is kept only as a fallback for admin session search;
        # device_name/last_active were exact-duplicate aliases of
        # device_label/last_active_at that no consumer ever read - removed.
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'device_label': self.device_label,
            # created_at/last_active_at are naive UTC datetimes (datetime.utcnow()).
            # isoformat() alone omits any timezone designator, so
            # `new Date(...)` on the frontend parsed it as LOCAL time instead
            # of UTC - on a UTC+5:30 browser a session active 4 minutes ago
            # would read as ~5.5 hours old. Appending 'Z' marks it as UTC.
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'last_active_at': self.last_active_at.isoformat() + 'Z' if self.last_active_at else None
        }

class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    username_attempted = db.Column(db.String(120), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(255), nullable=False)
    success = db.Column(db.Boolean, nullable=False)
    failure_reason = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username_attempted': self.username_attempted,
            'email_attempted': self.username_attempted,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'success': self.success,
            'failure_reason': self.failure_reason,
            # See DeviceSession.to_dict() above - naive UTC datetime, needs an
            # explicit 'Z' or the frontend misparses it as local time.
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'timestamp': self.created_at.isoformat() + 'Z' if self.created_at else None
        }

# Alias for backwards compatibility
LoginActivity = LoginAttempt
