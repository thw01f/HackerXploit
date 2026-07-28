from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Competition(db.Model):
    __tablename__ = 'competitions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(128), default='Online')
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    
    # Status: 'pending_approval', 'approved', 'rejected', 'completed'
    status = db.Column(db.String(32), default='pending_approval', nullable=False)
    
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Post event wrap-up data
    wrapup_notes = db.Column(db.Text, nullable=True)
    photos = db.Column(db.JSON, default=list)
    certificates = db.Column(db.JSON, default=list)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'created_by_id': self.created_by_id,
            'approved_by_id': self.approved_by_id,
            'wrapup_notes': self.wrapup_notes,
            'photos': self.photos or [],
            'certificates': self.certificates or [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CompetitionApplication(db.Model):
    __tablename__ = 'competition_applications'

    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(32), default='pending', nullable=False)  # pending, verified, rejected
    verified_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'competition_id': self.competition_id,
            'user_id': self.user_id,
            'status': self.status,
            'verified_by_id': self.verified_by_id,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None
        }
