from datetime import datetime
from app.models.user import db


class SiteFeatureToggle(db.Model):
    __tablename__ = 'site_feature_toggles'

    id = db.Column(db.Integer, primary_key=True)
    general_chat_enabled = db.Column(db.Boolean, default=True, nullable=False)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'general_chat_enabled': self.general_chat_enabled,
            'updated_by_id': self.updated_by_id,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    reported_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    target_type = db.Column(db.String(32), nullable=False)  # opportunity | comment | chat_message
    target_id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    resolved = db.Column(db.Boolean, default=False, index=True)
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'reported_by_id': self.reported_by_id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved': self.resolved,
            'resolved_by_id': self.resolved_by_id
        }

class EmailLog(db.Model):
    __tablename__ = 'email_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    type = db.Column(db.String(32), nullable=False)  # verify | approved | rejected | inbox_notify
    sent_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    delivered = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered': self.delivered
        }
