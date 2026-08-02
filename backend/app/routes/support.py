from flask import Blueprint, request, jsonify, g
from app.models import db, User, BugReport, ContactInquiry
from app.utils.decorators import require_auth, require_role, log_audit

support_bp = Blueprint('support', __name__, url_prefix='/api/support')

@support_bp.route('/contact', methods=['POST'])
@require_auth
def submit_contact_inquiry():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    subject = data.get('subject', '').strip()
    message = data.get('message', '').strip()

    if not name or not email or not subject or not message:
        return jsonify({'error': 'All fields (name, email, subject, message) are required'}), 400

    inquiry = ContactInquiry(
        user_id=g.current_user.id,
        name=name,
        email=email,
        subject=subject,
        message=message
    )
    db.session.add(inquiry)
    db.session.commit()

    log_audit('CONTACT_INQUIRY_SUBMITTED', target_type='ContactInquiry', target_id=inquiry.id, notes=f"Support message from {email}: {subject}")

    return jsonify({
        'message': 'Your support inquiry has been submitted successfully. Our team will get back to you shortly.',
        'inquiry': inquiry.to_dict()
    }), 201

@support_bp.route('/bug-report', methods=['POST'])
@require_auth
def submit_bug_report():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    category = data.get('category', 'UI/UX').strip()
    severity = data.get('severity', 'Low').strip()
    description = data.get('description', '').strip()
    steps = data.get('steps_to_reproduce', '').strip()

    if not title or not description:
        return jsonify({'error': 'Title and Description are required'}), 400

    bug = BugReport(
        user_id=g.current_user.id,
        user_name=g.current_user.full_name or g.current_user.username,
        user_email=g.current_user.email,
        title=title,
        category=category if category in ['UI/UX', 'Backend API', 'CTFd Sync', 'ID Card/QR', 'Security Vulnerability', 'Other'] else 'Other',
        severity=severity if severity in ['Low', 'Medium', 'High', 'Critical'] else 'Low',
        description=description,
        steps_to_reproduce=steps
    )
    db.session.add(bug)
    db.session.commit()

    log_audit('BUG_REPORT_SUBMITTED', target_type='BugReport', target_id=bug.id, notes=f"[{severity}] Bug reported by @{g.current_user.username}: {title}")

    return jsonify({
        'message': 'Bug report submitted successfully! Thank you for helping keep HackerXploit secure and functional.',
        'bug_report': bug.to_dict()
    }), 201

@support_bp.route('/my-reports', methods=['GET'])
@require_auth
def get_my_bug_reports():
    reports = BugReport.query.filter_by(user_id=g.current_user.id).order_by(BugReport.created_at.desc()).all()
    inquiries = ContactInquiry.query.filter_by(user_id=g.current_user.id).order_by(ContactInquiry.created_at.desc()).all()

    return jsonify({
        'bug_reports': [b.to_dict() for b in reports],
        'inquiries': [i.to_dict() for i in inquiries]
    }), 200

# Administrative endpoints
@support_bp.route('/admin/bug-reports', methods=['GET'])
@require_role('admin', 'root_admin')
def get_all_bug_reports():
    reports = BugReport.query.order_by(BugReport.created_at.desc()).all()
    inquiries = ContactInquiry.query.order_by(ContactInquiry.created_at.desc()).all()

    return jsonify({
        'bug_reports': [b.to_dict() for b in reports],
        'inquiries': [i.to_dict() for i in inquiries]
    }), 200

@support_bp.route('/admin/bug-reports/<int:report_id>/status', methods=['PUT'])
@require_role('admin', 'root_admin')
def update_bug_report_status(report_id):
    bug = BugReport.query.get_or_404(report_id)
    data = request.get_json() or {}
    
    if 'status' in data and data['status'] in ['open', 'in_review', 'resolved']:
        bug.status = data['status']
    if 'admin_notes' in data:
        bug.admin_notes = data['admin_notes'].strip()

    db.session.commit()
    log_audit('BUG_REPORT_STATUS_UPDATED', target_type='BugReport', target_id=bug.id, notes=f"Status set to {bug.status} for #{bug.id}")

    return jsonify(bug.to_dict()), 200
