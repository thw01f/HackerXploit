from datetime import datetime
from app.models import db

# Catalog of external industry certifications (e.g. CompTIA Security+, OSCP,
# CEH) that students can browse and pursue. Distinct from the existing
# Certificate model, which records a PDF this platform generates when a user
# completes one of its own courses/competitions - this one is purely
# informational content managed by teachers/admins, with no per-user record.
class CertificationCategory(db.Model):
    __tablename__ = 'certification_categories'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(128), unique=True, nullable=False, index=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    certifications = db.relationship('Certification', backref='category', order_by='Certification.id')

    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'title': self.title,
            'description': self.description or '',
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
            'certifications_count': len(self.certifications)
        }


class Certification(db.Model):
    __tablename__ = 'certifications'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('certification_categories.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(128), nullable=False)
    provider = db.Column(db.String(128), nullable=True)
    description = db.Column(db.Text, nullable=True)
    exam_link = db.Column(db.String(512), nullable=True)
    cover_image = db.Column(db.String(255), nullable=True)
    difficulty = db.Column(db.String(32), default='Intermediate')  # 'Entry-level', 'Beginner', 'Intermediate', 'Advanced'
    status = db.Column(db.String(20), default='published')  # 'draft' or 'published'
    position_x = db.Column(db.Float, nullable=True)
    position_y = db.Column(db.Float, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = db.relationship('User', foreign_keys=[author_id])

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'title': self.title,
            'provider': self.provider or '',
            'description': self.description or '',
            'exam_link': self.exam_link or '',
            'cover_image': self.cover_image or '/default-cover.svg',
            'difficulty': self.difficulty or 'Intermediate',
            'status': self.status,
            'position_x': self.position_x,
            'position_y': self.position_y,
            'author_id': self.author_id,
            'author_name': self.author.full_name if self.author else 'HackerXploit Team',
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None
        }


# Flowchart connections between certifications within the same category (e.g.
# Security+ -> CySA+ -> CASP+), drawn by hand in the Certification Studio -
# mirrors RoadmapEdge.
class CertificationEdge(db.Model):
    __tablename__ = 'certification_edges'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('certification_categories.id', ondelete='CASCADE'), nullable=False)
    source_cert_id = db.Column(db.Integer, db.ForeignKey('certifications.id', ondelete='CASCADE'), nullable=False)
    target_cert_id = db.Column(db.Integer, db.ForeignKey('certifications.id', ondelete='CASCADE'), nullable=False)
    label = db.Column(db.String(128), nullable=True)
    order_index = db.Column(db.Integer, default=1)

    __table_args__ = (
        db.UniqueConstraint('source_cert_id', 'target_cert_id', name='_cert_edge_source_target_uc'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'source_cert_id': self.source_cert_id,
            'target_cert_id': self.target_cert_id,
            'label': self.label,
            'order_index': self.order_index
        }
