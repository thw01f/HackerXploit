from datetime import datetime
from app.models.user import db


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    scope = db.Column(db.String(64), default='individual')  # individual | all_members | role:teacher | role:member | custom_list
    allow_reply = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'subject': self.subject,
            'body': self.body,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'scope': self.scope,
            'allow_reply': self.allow_reply
        }

class MessageRecipient(db.Model):
    __tablename__ = 'message_recipients'

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    is_read = db.Column(db.Boolean, default=False, index=True)
    read_at = db.Column(db.DateTime, nullable=True)
    is_archived = db.Column(db.Boolean, default=False, index=True)
    is_deleted_by_recipient = db.Column(db.Boolean, default=False, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'message_id': self.message_id,
            'user_id': self.user_id,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'is_archived': self.is_archived,
            'is_deleted_by_recipient': self.is_deleted_by_recipient
        }
