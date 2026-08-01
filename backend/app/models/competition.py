from datetime import datetime
from app.models.user import db

class Competition(db.Model):
    __tablename__ = 'competitions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    poster_image = db.Column(db.String(256), nullable=True)
    external_link = db.Column(db.String(256), nullable=True)
    
    starts_at = db.Column(db.DateTime, nullable=False)
    ends_at = db.Column(db.DateTime, nullable=False)
    application_deadline = db.Column(db.DateTime, nullable=True)
    
    # category: ctf | hackathon | workshop | other
    category = db.Column(db.String(32), default='ctf', nullable=False)
    # priority: high | medium | normal
    priority = db.Column(db.String(16), default='normal', nullable=False)
    
    posted_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    # status: upcoming | ongoing | ended
    status = db.Column(db.String(32), default='upcoming', nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to participations
    participations = db.relationship('CompetitionParticipation', backref='competition', lazy=True, cascade='all, delete-orphan')

    # Backward compatibility helper properties
    @property
    def start_date(self):
        return self.starts_at

    @property
    def end_date(self):
        return self.ends_at

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'poster_image': self.poster_image,
            'external_link': self.external_link,
            'starts_at': self.starts_at.isoformat() if self.starts_at else None,
            'ends_at': self.ends_at.isoformat() if self.ends_at else None,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'category': self.category,
            'priority': self.priority,
            'posted_by_id': self.posted_by_id,
            'status': self.status,
            'is_archived': self.is_archived,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CompetitionParticipation(db.Model):
    __tablename__ = 'competition_participation'

    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    application_screenshot = db.Column(db.String(256), nullable=True)
    # application_status: pending_verification | verified | rejected
    application_status = db.Column(db.String(32), default='pending_verification', nullable=False)
    
    verified_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    
    # result: participated | winner | runner_up | not_selected
    result = db.Column(db.String(32), default='participated', nullable=True)
    placement_label = db.Column(db.String(64), nullable=True)  # e.g., "1st Place", "Top 10 Finalist"
    certificate_file = db.Column(db.String(256), nullable=True)
    event_photos = db.Column(db.JSON, default=list)  # list of photo URLs
    summary_notes = db.Column(db.Text, nullable=True)
    
    submitted_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'competition_id': self.competition_id,
            'user_id': self.user_id,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'application_screenshot': self.application_screenshot,
            'application_status': self.application_status,
            'verified_by_id': self.verified_by_id,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'result': self.result,
            'placement_label': self.placement_label,
            'certificate_file': self.certificate_file,
            'event_photos': self.event_photos or [],
            'summary_notes': self.summary_notes,
            'submitted_by_id': self.submitted_by_id,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }

# Alias for backward compatibility
CompetitionApplication = CompetitionParticipation

class EventAttendance(db.Model):
    __tablename__ = 'event_attendance'

    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    scanned_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    scanned_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(32), default='present', nullable=False)  # present | approved | late
    remark = db.Column(db.Text, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('competition_id', 'user_id', name='uq_event_user_attendance'),
    )

    def to_dict(self):
        from app.models.user import User
        user = User.query.get(self.user_id)
        scanned_by = User.query.get(self.scanned_by_id) if self.scanned_by_id else None
        return {
            'id': self.id,
            'competition_id': self.competition_id,
            'user_id': self.user_id,
            'user_full_name': (user.full_name or user.username) if user else 'Unknown',
            'user_username': user.username if user else 'Unknown',
            'user_email': user.email if user else None,
            'user_avatar_url': user.avatar_url if user else None,
            'user_member_id': f'HX-2026-{user.id:04d}' if user else None,
            'user_academic_year': getattr(user, 'academic_year', None) if user else None,
            'user_department': getattr(user, 'department', None) if user else None,
            'scanned_by_id': self.scanned_by_id,
            'scanned_by_name': (scanned_by.full_name or scanned_by.username) if scanned_by else 'Self/System',
            'scanned_at': self.scanned_at.isoformat() if self.scanned_at else None,
            'status': self.status,
            'remark': self.remark
        }


class ClubEventFeedback(db.Model):
    __tablename__ = 'club_event_feedback'

    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)  # 1 to 5 stars
    feedback_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('competition_id', 'user_id', name='uq_event_user_feedback'),
    )

    def to_dict(self):
        from app.models.user import User
        user = User.query.get(self.user_id)
        return {
            'id': self.id,
            'competition_id': self.competition_id,
            'user_id': self.user_id,
            'user_full_name': (user.full_name or user.username) if user else 'Anonymous',
            'user_username': user.username if user else 'Anonymous',
            'user_avatar_url': user.avatar_url if user else None,
            'user_member_id': user.member_id if user else None,
            'rating': self.rating,
            'feedback_text': self.feedback_text,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
