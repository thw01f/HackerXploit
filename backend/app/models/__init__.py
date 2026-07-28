from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User, PasswordResetRequest, PasswordResetCode, ProfileFieldDefinition, UserProfileValue
from .session import DeviceSession, LoginAttempt, LoginActivity
from .audit import AuditLog
from .academy import Course, Module, Lesson, CourseEnrollment
from .competition import Competition, CompetitionApplication
from .opportunity import Opportunity, OpportunityApplication
from .chat import ChatMessage, Notification
from .oauth import OAuth2Client, OAuth2AuthorizationCode, OAuth2Token

__all__ = [
    'db',
    'User',
    'PasswordResetRequest',
    'PasswordResetCode',
    'ProfileFieldDefinition',
    'UserProfileValue',
    'DeviceSession',
    'LoginAttempt',
    'LoginActivity',
    'AuditLog',
    'Course',
    'Module',
    'Lesson',
    'CourseEnrollment',
    'Competition',
    'CompetitionApplication',
    'Opportunity',
    'OpportunityApplication',
    'ChatMessage',
    'Notification',
    'OAuth2Client',
    'OAuth2AuthorizationCode',
    'OAuth2Token'
]
