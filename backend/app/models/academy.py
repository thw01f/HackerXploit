from datetime import datetime
from app.models import db

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(128), unique=True, nullable=False, index=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cover_image = db.Column(db.String(255), nullable=True)
    difficulty = db.Column(db.String(32), default='Easy')  # 'Easy', 'Intermediate', 'Advanced'
    is_new = db.Column(db.Boolean, default=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    status = db.Column(db.String(20), default='published')  # 'draft' or 'published'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chapters = db.relationship('CourseChapter', backref='course', cascade='all, delete-orphan', order_by='CourseChapter.order_index')
    enrollments = db.relationship('Enrollment', backref='course', cascade='all, delete-orphan')
    comments = db.relationship('CourseComment', backref='course', cascade='all, delete-orphan')
    author = db.relationship('User', foreign_keys=[author_id])

    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'title': self.title,
            'description': self.description,
            'cover_image': self.cover_image or '/uploads/courses/default_cover.png',
            'difficulty': self.difficulty or 'Easy',
            'is_new': self.is_new,
            'author_id': self.author_id,
            'author_name': self.author.full_name if self.author else 'HackerXploit Team',
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'chapters_count': len(self.chapters)
        }

class CourseChapter(db.Model):
    __tablename__ = 'course_chapters'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    order_index = db.Column(db.Integer, default=1)
    title = db.Column(db.String(128), nullable=False)
    content_markdown = db.Column(db.Text, nullable=False)
    attachments = db.Column(db.JSON, default=list)  # List of dicts: [{"name": "lab.zip", "path": "/var/uploads/protected/lab.zip"}]

    comments = db.relationship('CourseComment', backref='chapter', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'order_index': self.order_index,
            'title': self.title,
            'content_markdown': self.content_markdown,
            'attachments': self.attachments or []
        }

class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    progress_percent = db.Column(db.Float, default=0.0)
    completed_chapters = db.Column(db.JSON, default=list)  # List of chapter IDs
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('enrollments', cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'progress_percent': round(self.progress_percent, 1),
            'completed_chapters': self.completed_chapters or [],
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Alias for backward compatibility across existing blueprints
CourseEnrollment = Enrollment

class CourseComment(db.Model):
    __tablename__ = 'course_comments'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('course_chapters.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_reported = db.Column(db.Boolean, default=False)

    user = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'chapter_id': self.chapter_id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Anonymous',
            'avatar_url': self.user.avatar_url if self.user else '/uploads/avatars/default.png',
            'body': self.body,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_reported': self.is_reported
        }

class LiveClass(db.Model):
    __tablename__ = 'live_classes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    meeting_link = db.Column(db.String(255), nullable=False)
    thumbnail_url = db.Column(db.String(255), nullable=True)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    instructor = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'meeting_link': self.meeting_link,
            'thumbnail_url': self.thumbnail_url or '/uploads/courses/default_cover.png',
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'duration_minutes': self.duration_minutes,
            'instructor_id': self.instructor_id,
            'instructor_name': self.instructor.full_name if self.instructor else 'HackerXploit Staff',
            'instructor_avatar': self.instructor.avatar_url if self.instructor else '/uploads/avatars/default.png',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
