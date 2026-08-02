from datetime import datetime
from app.models import db

class BugReport(db.Model):
    __tablename__ = 'bug_reports'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    user_name = db.Column(db.String(120), nullable=True)
    user_email = db.Column(db.String(120), nullable=True)

    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(64), default='UI/UX', nullable=False) # 'UI/UX', 'Backend API', 'CTFd Sync', 'ID Card/QR', 'Security Vulnerability', 'Other'
    severity = db.Column(db.String(32), default='Low', nullable=False) # 'Low', 'Medium', 'High', 'Critical'
    description = db.Column(db.Text, nullable=False)
    steps_to_reproduce = db.Column(db.Text, nullable=True)
    
    # Status: 'open', 'in_review', 'resolved'
    status = db.Column(db.String(32), default='open', nullable=False)
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_email': self.user_email,
            'title': self.title,
            'category': self.category,
            'severity': self.severity,
            'description': self.description,
            'steps_to_reproduce': self.steps_to_reproduce,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ContactInquiry(db.Model):
    __tablename__ = 'contact_inquiries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Status: 'open', 'responded'
    status = db.Column(db.String(32), default='open', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'subject': self.subject,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
