from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User, PasswordResetRequest, PasswordResetCode, ProfileFieldDefinition, UserProfileValue
from .session import DeviceSession, LoginAttempt, LoginActivity
from .audit import AuditLog
from .academy import Course, CourseChapter, CourseModule, ModuleNote, Enrollment, CourseEnrollment, CourseComment, CourseResource, NoteRating
from .certificate import Certificate
from .certification import Certification, CertificationCategory, CertificationEdge
from .competition import Competition, CompetitionParticipation, CompetitionApplication, EventAttendance, ClubEventFeedback
from .retention import RetentionSettings
from .opportunity import Opportunity, OpportunityApplication, Skill, member_skills, opportunity_skills
from .chat import ChatMessage, Notification, NotificationPreference
from .oauth import OAuth2Client, OAuth2AuthorizationCode, OAuth2Token
from .activity import ActivitySession, ActivityHeartbeat
from .moderation import SiteFeatureToggle, Report, EmailLog, Announcement
from .inbox import Message, MessageRecipient
from .portfolio_privacy_backup import PublicProfileSetting, BackupRecord, IDCardToken

from .support import BugReport, ContactInquiry
from .roadmap import Roadmap, RoadmapNode, RoadmapNodeResource, RoadmapEdge, UserRoadmapProgress

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
    'CourseModule',
    'ModuleNote',
    'Enrollment',
    'CourseEnrollment',
    'CourseComment',
    'CourseResource',
    'NoteRating',
    'Certificate',
    'Certification',
    'CertificationCategory',
    'CertificationEdge',
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
    'NotificationPreference',
    'OAuth2Client',
    'OAuth2AuthorizationCode',
    'OAuth2Token',
    'ActivitySession',
    'ActivityHeartbeat',
    'SiteFeatureToggle',
    'Report',
    'EmailLog',
    'Announcement',
    'Message',
    'MessageRecipient',
    'PublicProfileSetting',
    'BackupRecord',
    'IDCardToken',
    'BugReport',
    'ContactInquiry'
]



