from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User, PasswordResetRequest, PasswordResetCode, ProfileFieldDefinition, UserProfileValue
from .session import DeviceSession, LoginAttempt, LoginActivity
from .audit import AuditLog
from .academy import Course, CourseChapter, Enrollment, CourseEnrollment, CourseComment
from .certificate import Certificate
from .competition import Competition, CompetitionParticipation, CompetitionApplication
from .retention import RetentionSettings
from .opportunity import Opportunity, OpportunityApplication, Skill, member_skills, opportunity_skills
from .chat import ChatMessage, Notification
from .oauth import OAuth2Client, OAuth2AuthorizationCode, OAuth2Token
from .activity import ActivitySession, ActivityHeartbeat
from .moderation import SiteFeatureToggle, Report, EmailLog
from .inbox import Message, MessageRecipient
from .portfolio_privacy_backup import PublicProfileSetting, BackupRecord, IDCardToken

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
    'CourseChapter',
    'Enrollment',
    'CourseEnrollment',
    'CourseComment',
    'Certificate',
    'Competition',
    'CompetitionParticipation',
    'CompetitionApplication',
    'RetentionSettings',
    'Opportunity',
    'OpportunityApplication',
    'Skill',
    'member_skills',
    'opportunity_skills',
    'ChatMessage',
    'Notification',
    'OAuth2Client',
    'OAuth2AuthorizationCode',
    'OAuth2Token',
    'ActivitySession',
    'ActivityHeartbeat',
    'SiteFeatureToggle',
    'Report',
    'EmailLog',
    'Message',
    'MessageRecipient',
    'PublicProfileSetting',
    'BackupRecord',
    'IDCardToken'
]



