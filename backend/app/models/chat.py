from datetime import datetime
from app.models.user import db


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(32), default='general', index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    deleted_by_role = db.Column(db.String(32), nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        from app.models.user import User
        if self.is_deleted:
            deleter_name = "Moderator"
            if self.deleted_by_id:
                deleter = User.query.get(self.deleted_by_id)
                if deleter:
                    deleter_name = deleter.full_name or deleter.username
            role_str = f" ({self.deleted_by_role})" if self.deleted_by_role else ""
            display_content = f"Message deleted by {deleter_name}{role_str}"
        else:
            display_content = self.content

        return {
            'id': self.id,
            'channel': self.channel,
            'user_id': self.user_id,
            'content': display_content,
            'is_deleted': self.is_deleted,
            'deleted_by_id': self.deleted_by_id,
            'deleted_by_role': self.deleted_by_role,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class NotificationPreference(db.Model):
    __tablename__ = 'notification_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)

    # Each toggle controls whether a category ALSO sends an email, on top of
    # the in-app notification bell (which always fires - these are additive,
    # not a mute switch for the whole category).
    email_inbox_messages = db.Column(db.Boolean, default=True, nullable=False)
    email_announcements = db.Column(db.Boolean, default=False, nullable=False)
    email_account_updates = db.Column(db.Boolean, default=True, nullable=False)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_or_create(user_id):
        pref = NotificationPreference.query.filter_by(user_id=user_id).first()
        if not pref:
            pref = NotificationPreference(user_id=user_id)
            db.session.add(pref)
            db.session.commit()
        return pref

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'email_inbox_messages': self.email_inbox_messages,
            'email_announcements': self.email_announcements,
            'email_account_updates': self.email_account_updates,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    type = db.Column(db.String(64), default='system')  # inbox | system | approval
    title = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'body': self.message,
            'link': self.link,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
