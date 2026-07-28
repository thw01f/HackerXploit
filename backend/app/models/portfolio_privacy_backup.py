from datetime import datetime
from app.models.user import db

class PublicProfileSetting(db.Model):
    __tablename__ = 'public_profile_settings'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    is_public = db.Column(db.Boolean, default=False, nullable=False)
    show_activity_hours = db.Column(db.Boolean, default=True, nullable=False)
    show_certificates = db.Column(db.Boolean, default=True, nullable=False)

    user = db.relationship('User', backref=db.backref('public_profile_settings', uselist=False, cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'is_public': self.is_public,
            'show_activity_hours': self.show_activity_hours,
            'show_certificates': self.show_certificates
        }

class BackupRecord(db.Model):
    __tablename__ = 'backups'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    size_bytes = db.Column(db.BigInteger, nullable=False, default=0)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    type = db.Column(db.String(32), default='manual', nullable=False) # manual | scheduled

    created_by = db.relationship('User', backref='created_backups')

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'size_bytes': self.size_bytes,
            'created_by_id': self.created_by_id,
            'created_by_username': self.created_by.username if self.created_by else 'System / Celery Beat',
            'created_at': self.created_at.isoformat(),
            'type': self.type
        }

class IDCardToken(db.Model):
    __tablename__ = 'id_card_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    revoked_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref=db.backref('id_card_tokens', cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'token': self.token,
            'created_at': self.created_at.isoformat(),
            'revoked_at': self.revoked_at.isoformat() if self.revoked_at else None,
            'is_valid': self.revoked_at is None
        }
