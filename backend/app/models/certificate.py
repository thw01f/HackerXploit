from datetime import datetime
from app.models import db

class Certificate(db.Model):
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    type = db.Column(db.String(32), nullable=False)  # 'course_completion' or 'competition'
    source_id = db.Column(db.Integer, nullable=False)  # course_id or competition_id
    file_path = db.Column(db.String(255), nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('certificates', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'source_id': self.source_id,
            'file_path': self.file_path,
            'issued_at': self.issued_at.isoformat() if self.issued_at else None
        }
