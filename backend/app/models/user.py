from datetime import datetime, timedelta
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.models import db

ph = PasswordHasher()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=True, default='')
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Roles: 'admin', 'teacher', 'member'
    role = db.Column(db.String(32), default='member', nullable=False)
    is_root_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # Status: 'pending', 'approved', 'rejected', 'suspended'
    status = db.Column(db.String(32), default='pending', nullable=False)
    is_first_login = db.Column(db.Boolean, default=False, nullable=False)
    
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    student_id = db.Column(db.String(64), nullable=True)
    graduation_year = db.Column(db.Integer, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    avatar_url = db.Column(db.String(255), default='/uploads/avatars/default.png')
    skills = db.Column(db.JSON, default=list)
    
    failed_login_count = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    oauth_ctfd_synced = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, nullable=True)
    last_seen_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        if self.is_locked():
            return False
        try:
            ph.verify(self.password_hash, password)
            self.failed_login_count = 0
            self.locked_until = None
            return True
        except VerifyMismatchError:
            self.failed_login_count += 1
            if self.failed_login_count >= 5:
                self.locked_until = datetime.utcnow() + timedelta(minutes=15)
            return False

    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        if self.locked_until and self.locked_until <= datetime.utcnow():
            self.locked_until = None
            self.failed_login_count = 0
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name or self.username,
            'role': 'root_admin' if self.is_root_admin else self.role,
            'is_root_admin': self.is_root_admin,
            'status': self.status,
            'is_first_login': self.is_first_login,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'student_id': self.student_id,
            'graduation_year': self.graduation_year,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'skills': self.skills or [],
            'failed_login_count': self.failed_login_count,
            'locked_until': self.locked_until.isoformat() if self.locked_until else None,
            'is_locked': self.is_locked(),
            'oauth_ctfd_synced': self.oauth_ctfd_synced,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'last_seen_at': self.last_seen_at.isoformat() if self.last_seen_at else None
        }

class PasswordResetRequest(db.Model):
    __tablename__ = 'password_reset_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(32), default='pending', nullable=False) # 'pending', 'fulfilled', 'expired'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PasswordResetCode(db.Model):
    __tablename__ = 'password_reset_codes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    code = db.Column(db.String(32), nullable=False, index=True)
    issued_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)

    def is_valid(self):
        return self.used_at is None and datetime.utcnow() < self.expires_at

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'code': self.code,
            'issued_by_admin_id': self.issued_by_admin_id,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'is_valid': self.is_valid()
        }

class ProfileFieldDefinition(db.Model):
    __tablename__ = 'profile_field_definitions'

    id = db.Column(db.Integer, primary_key=True)
    field_key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    label = db.Column(db.String(128), nullable=False)
    field_type = db.Column(db.String(32), default='text', nullable=False) # 'text', 'number', 'date', 'select', 'file'
    options = db.Column(db.JSON, default=list) # Options for 'select'
    required = db.Column(db.Boolean, default=False, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'field_key': self.field_key,
            'label': self.label,
            'field_type': self.field_type,
            'options': self.options or [],
            'required': self.required,
            'active': self.active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserProfileValue(db.Model):
    __tablename__ = 'user_profile_values'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey('profile_field_definitions.id', ondelete='CASCADE'), nullable=False)
    value = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'field_id': self.field_id,
            'value': self.value,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
