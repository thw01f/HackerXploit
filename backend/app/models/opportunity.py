from datetime import datetime
from app.models.user import db

# Junction Table for Member Skills
member_skills = db.Table(
    'member_skills',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True)
)

# Junction Table for Opportunity Skills
opportunity_skills = db.Table(
    'opportunity_skills',
    db.Column('opportunity_id', db.Integer, db.ForeignKey('opportunities.id', ondelete='CASCADE'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True)
)

class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Opportunity(db.Model):
    __tablename__ = 'opportunities'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    company = db.Column(db.String(128), nullable=False)
    type = db.Column(db.String(32), default='internship', nullable=False)  # internship | job
    description = db.Column(db.Text, nullable=False)
    apply_link = db.Column(db.String(256), nullable=True)
    location = db.Column(db.String(128), default='Remote')
    deadline = db.Column(db.DateTime, nullable=True)
    posted_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    status = db.Column(db.String(32), default='open', nullable=False)  # open | closed

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    skills = db.relationship('Skill', secondary=opportunity_skills, lazy='subquery',
                             backref=db.backref('opportunities', lazy=True))

    @property
    def organization(self):
        return self.company

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'organization': self.company,
            'type': self.type,
            'description': self.description,
            'apply_link': self.apply_link,
            'location': self.location,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'posted_by_id': self.posted_by_id,
            'status': self.status,
            'skills': [s.to_dict() for s in self.skills],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class OpportunityApplication(db.Model):
    __tablename__ = 'opportunity_applications'

    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    resume_url = db.Column(db.String(255), nullable=True)
    cover_letter = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(32), default='submitted')
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
