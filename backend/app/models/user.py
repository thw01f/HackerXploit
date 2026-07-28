from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

class User(SQLAlchemy().Model):
    __tablename__ = 'users'

    id = SQLAlchemy().Column(SQLAlchemy().Integer, primary_key=True)
    username = SQLAlchemy().Column(SQLAlchemy().String(64), unique=True, nullable=False, index=True)
    email = SQLAlchemy().Column(SQLAlchemy().String(120), unique=True, nullable=False, index=True)
    full_name = SQLAlchemy().Column(SQLAlchemy().String(120), nullable=False)
    password_hash = SQLAlchemy().Column(SQLAlchemy().String(255), nullable=False)
    
    # Roles: 'root_admin', 'admin', 'teacher', 'member'
    role = SQLAlchemy().Column(SQLAlchemy().String(32), default='member', nullable=False)
    
    # Status: 'pending', 'approved', 'suspended', 'rejected'
    status = SQLAlchemy().Column(SQLAlchemy().String(32), default='pending', nullable=False)
    
    student_id = SQLAlchemy().Column(SQLAlchemy().String(64), nullable=True)
    graduation_year = SQLAlchemy().Column(SQLAlchemy().Integer, nullable=True)
    bio = SQLAlchemy().Column(SQLAlchemy().Text, nullable=True)
    avatar_url = SQLAlchemy().Column(SQLAlchemy().String(255), default='/uploads/avatars/default.png')
    skills = SQLAlchemy().Column(SQLAlchemy().JSON, default=list)
    
    failed_login_attempts = SQLAlchemy().Column(SQLAlchemy().Integer, default=0)
    locked_until = SQLAlchemy().Column(SQLAlchemy().DateTime, nullable=True)
    
    created_at = SQLAlchemy().Column(SQLAlchemy().DateTime, default=datetime.utcnow)
    updated_at = SQLAlchemy().Column(SQLAlchemy().DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        if self.is_locked():
            return False
        try:
            ph.verify(self.password_hash, password)
            self.failed_login_attempts = 0
            self.locked_until = None
            return True
        except VerifyMismatchError:
            self.failed_login_attempts += 1
            if self.failed_login_attempts >= 5:
                self.locked_until = datetime.utcnow() + timedelta(minutes=15)
            return False

    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        if self.locked_until and self.locked_until <= datetime.utcnow():
            self.locked_until = None
            self.failed_login_attempts = 0
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'status': self.status,
            'student_id': self.student_id,
            'graduation_year': self.graduation_year,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'skills': self.skills or [],
            'is_locked': self.is_locked(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
