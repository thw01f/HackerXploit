from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Opportunity(db.Model):
    __tablename__ = 'opportunities'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    organization = db.Column(db.String(128), nullable=False)
    type = db.Column(db.String(32), default='Internship')  # Internship, Research, CTF Team, Job
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(128), default='Remote')
    deadline = db.Column(db.DateTime, nullable=True)
    posted_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'organization': self.organization,
            'type': self.type,
            'description': self.description,
            'location': self.location,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'posted_by_id': self.posted_by_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class OpportunityApplication(db.Model):
    __tablename__ = 'opportunity_applications'

    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    resume_url = db.Column(db.String(255), nullable=True)
    cover_letter = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(32), default='submitted')  # submitted, under_review, accepted, rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'opportunity_id': self.opportunity_id,
            'user_id': self.user_id,
            'resume_url': self.resume_url,
            'cover_letter': self.cover_letter,
            'status': self.status,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None
        }
