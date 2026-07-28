from datetime import datetime
from app.models.user import db

class RetentionSettings(db.Model):
    __tablename__ = 'retention_settings'

    id = db.Column(db.Integer, primary_key=True)
    # competitions_auto_delete: never | 1_month | 3_month | 6_month
    competitions_auto_delete = db.Column(db.String(32), default='never', nullable=False)
    # competitions_delete_mode: hard_delete | archive
    competitions_delete_mode = db.Column(db.String(32), default='archive', nullable=False)
    
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'competitions_auto_delete': self.competitions_auto_delete,
            'competitions_delete_mode': self.competitions_delete_mode,
            'updated_by_id': self.updated_by_id,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
