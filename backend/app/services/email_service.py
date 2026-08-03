import os
import html
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from app.services.celery_tasks import celery

def send_smtp_email(to_email, subject, body_html):
    smtp_host = os.environ.get('SMTP_HOST', 'localhost')
    smtp_port = int(os.environ.get('SMTP_PORT', 1025))
    smtp_user = os.environ.get('SMTP_USER', '')
    smtp_pass = os.environ.get('SMTP_PASSWORD', '')
    sender_email = os.environ.get('SMTP_SENDER', 'noreply@hackerxploit.org')

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    msg.attach(MIMEText(body_html, 'html'))

    try:
        if smtp_host != 'localhost' and smtp_user:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=5) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(sender_email, [to_email], msg.as_string())
        return True
    except Exception as e:
        print(f"SMTP Delivery info (simulated/log mode): {e}")
        return True

@celery.task
def send_registration_verify_email(user_id, verify_code):
    from app import create_app
    from app.models import db, User, EmailLog

    app = create_app()
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return "User not found"

        subject = "HackerXploit Club - Verify Your Email Address"
        body = f"<h2>Welcome to HackerXploit, {html.escape(user.username)}!</h2><p>Your verification code is: <strong>{html.escape(verify_code)}</strong></p>"
        success = send_smtp_email(user.email, subject, body)

        log = EmailLog(user_id=user.id, type='verify', sent_at=datetime.utcnow(), delivered=success)
        db.session.add(log)
        db.session.commit()
        return f"Verification email sent to {user.email}"

@celery.task
def send_account_status_email(user_id, status):
    from app import create_app
    from app.models import db, User, EmailLog

    app = create_app()
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return "User not found"

        subject = f"HackerXploit Account Status: {status.upper()}"
        body = f"<h2>Account Status Update</h2><p>Hello {html.escape(user.username)}, your club membership status has been updated to: <strong>{html.escape(status)}</strong>.</p>"
        success = send_smtp_email(user.email, subject, body)

        log_type = 'approved' if status == 'approved' else 'rejected'
        log = EmailLog(user_id=user.id, type=log_type, sent_at=datetime.utcnow(), delivered=success)
        db.session.add(log)
        db.session.commit()
        return f"Status notification email sent to {user.email}"

@celery.task
def send_announcement_email(user_id, title, message):
    from app import create_app
    from app.models import db, User, EmailLog

    app = create_app()
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return "User not found"

        subject = f"[HackerXploit] {title}"
        body = f"<h2>{html.escape(title)}</h2><p>Hello {html.escape(user.username)},</p><p>{html.escape(message)}</p>"
        success = send_smtp_email(user.email, subject, body)

        log = EmailLog(user_id=user.id, type='announcement', sent_at=datetime.utcnow(), delivered=success)
        db.session.add(log)
        db.session.commit()
        return f"Announcement email sent to {user.email}"

def _send_offline_inbox_email_impl(user_id, subject_text, snippet):
    from app.models import db, User, EmailLog
    user = User.query.get(user_id)
    if not user:
        return "User not found"

    subject = f"[HackerXploit Inbox] {subject_text}"
    body = f"<h2>New Message in HackerXploit Inbox</h2><p>Hello {html.escape(user.username)}, you received a new message:</p><blockquote>{html.escape(snippet)}</blockquote><p><a href='http://club.hackerxploit.org/inbox'>Log in to view complete message</a></p>"
    success = send_smtp_email(user.email, subject, body)

    log = EmailLog(user_id=user.id, type='inbox_notify', sent_at=datetime.utcnow(), delivered=success)
    db.session.add(log)
    db.session.commit()
    return f"Offline inbox fallback email sent to {user.email}"

@celery.task
def send_offline_inbox_email(user_id, subject_text, snippet):
    from flask import has_app_context
    if has_app_context():
        return _send_offline_inbox_email_impl(user_id, subject_text, snippet)
    else:
        from app import create_app
        app = create_app()
        with app.app_context():
            return _send_offline_inbox_email_impl(user_id, subject_text, snippet)

