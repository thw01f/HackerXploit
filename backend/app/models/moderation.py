from datetime import datetime
from app.models.user import db


class SiteFeatureToggle(db.Model):
    __tablename__ = 'site_feature_toggles'

    id = db.Column(db.Integer, primary_key=True)
    general_chat_enabled = db.Column(db.Boolean, default=True, nullable=False)
    allowed_email_domains = db.Column(db.String(512), default="gmail.com,srm.edu.in,hackerxploit.org", nullable=True)
    password_min_length = db.Column(db.Integer, default=8, nullable=False)
    announcement_enabled = db.Column(db.Boolean, default=True, nullable=False)
    announcement_banner = db.Column(db.String(512), default="Welcome to HackerXploit Club Platform! Next CTF competition is scheduled for Saturday.", nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'general_chat_enabled': self.general_chat_enabled,
            'allowed_email_domains': self.allowed_email_domains or "gmail.com,srm.edu.in,hackerxploit.org",
            'password_min_length': self.password_min_length or 8,
            'announcement_enabled': self.announcement_enabled if self.announcement_enabled is not None else True,
            'announcement_banner': self.announcement_banner if self.announcement_banner is not None else "Welcome to HackerXploit Club Platform! Next CTF competition is scheduled for Saturday.",
            'updated_by_id': self.updated_by_id,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(512), nullable=False)
    # Optional CTA button, e.g. button_label="LAUNCH CTF ARENA", link="https://arena.hackerxploit.org"
    # Rendered as plain banner text when link is empty, as a clickable CTA when both are set.
    button_label = db.Column(db.String(64), nullable=True)
    link = db.Column(db.String(512), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'button_label': self.button_label,
            'link': self.link,
            'is_active': self.is_active,
            'display_order': self.display_order,
            'created_by_id': self.created_by_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
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
