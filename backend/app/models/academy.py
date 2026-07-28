from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    slug = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(64), default='General')
    difficulty = db.Column(db.String(32), default='Beginner')  # Beginner, Intermediate, Advanced
    thumbnail_url = db.Column(db.String(255), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    modules = db.relationship('Module', backref='course', cascade='all, delete-orphan', order_by='Module.order')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'category': self.category,
            'difficulty': self.difficulty,
            'thumbnail_url': self.thumbnail_url,
            'author_id': self.author_id,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'modules_count': len(self.modules)
        }

class Module(db.Model):
    __tablename__ = 'course_modules'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    order = db.Column(db.Integer, default=1)

    lessons = db.relationship('Lesson', backref='module', cascade='all, delete-orphan', order_by='Lesson.order')

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'order': self.order,
            'lessons': [l.to_dict() for l in self.lessons]
        }

class Lesson(db.Model):
    __tablename__ = 'course_lessons'

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('course_modules.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    content_markdown = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.String(255), nullable=True)
    attachment_url = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            'id': self.id,
            'module_id': self.module_id,
            'title': self.title,
            'content_markdown': self.content_markdown,
            'video_url': self.video_url,
            'attachment_url': self.attachment_url,
            'order': self.order
        }

class CourseEnrollment(db.Model):
    __tablename__ = 'course_enrollments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    completed_lessons = db.Column(db.JSON, default=list)  # List of lesson IDs
    is_completed = db.Column(db.Boolean, default=False)
    certificate_url = db.Column(db.String(255), nullable=True)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'completed_lessons': self.completed_lessons or [],
            'is_completed': self.is_completed,
            'certificate_url': self.certificate_url,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
