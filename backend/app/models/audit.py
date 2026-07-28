from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    actor_name = db.Column(db.String(120), nullable=False)
    actor_role = db.Column(db.String(32), nullable=False)
    action = db.Column(db.String(64), nullable=False, index=True)
    target_type = db.Column(db.String(64), nullable=True)
    target_id = db.Column(db.String(64), nullable=True)
    details = db.Column(db.JSON, default=dict)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'actor_id': self.actor_id,
            'actor_name': self.actor_name,
            'actor_role': self.actor_role,
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
