from datetime import datetime
from app.models import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    actor_name = db.Column(db.String(120), nullable=True)
    actor_role = db.Column(db.String(32), nullable=False)
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    target_type = db.Column(db.String(64), nullable=True)
    target_id = db.Column(db.String(64), nullable=True)
    action = db.Column(db.String(64), nullable=False, index=True)
    notes = db.Column(db.Text, nullable=True)
    details = db.Column(db.JSON, default=dict)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'actor_id': self.actor_id,
            'actor_name': self.actor_name or (f"User #{self.actor_id}" if self.actor_id else 'System'),
            'actor_role': self.actor_role,
            'target_user_id': self.target_user_id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'action': self.action,
            'notes': self.notes or (str(self.details) if self.details else ''),
            'details': self.details or {},
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'timestamp': self.created_at.isoformat() + 'Z' if self.created_at else None
        }
