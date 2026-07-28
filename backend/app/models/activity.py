from datetime import datetime
from app.models import db

class ActivitySession(db.Model):
    __tablename__ = 'activity_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    login_at = db.Column(db.DateTime, nullable=True)
    logout_at = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Integer, default=0, nullable=False)
    subdomain = db.Column(db.String(32), default='club', nullable=False)
    ip_address = db.Column(db.String(64), nullable=True)
    user_agent = db.Column(db.String(256), nullable=True)
    date = db.Column(db.String(10), nullable=False, index=True) # YYYY-MM-DD
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'login_at': self.login_at.isoformat() if self.login_at else None,
            'logout_at': self.logout_at.isoformat() if self.logout_at else None,
            'duration_seconds': self.duration_seconds,
            'duration_hours': round(self.duration_seconds / 3600.0, 2),
            'subdomain': self.subdomain,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'date': self.date,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ActivityHeartbeat(db.Model):
    __tablename__ = 'activity_heartbeats'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    subdomain = db.Column(db.String(32), default='club', nullable=False)
    ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subdomain': self.subdomain,
            'ts': self.ts.isoformat() if self.ts else None
        }
