from flask import Blueprint, request, jsonify, g
from app.models import db, Report, User, ChatMessage, CourseComment, Opportunity
from app.utils.decorators import require_role, log_audit

reports_bp = Blueprint('reports', __name__, url_prefix='/api/admin/reports')

@reports_bp.route('', methods=['GET'])
@require_role('teacher', 'admin', 'root_admin')
def get_reports_queue():
    status_filter = request.args.get('status', 'all')  # pending | resolved | all
    target_filter = request.args.get('target_type', 'all')  # opportunity | comment | chat_message | all

    query = Report.query

    if status_filter == 'pending':
        query = query.filter_by(resolved=False)
    elif status_filter == 'resolved':
        query = query.filter_by(resolved=True)

    if target_filter != 'all':
        query = query.filter_by(target_type=target_filter)

    reports = query.order_by(Report.created_at.desc()).all()

    items = []
    for rep in reports:
        reporter = User.query.get(rep.reported_by_id)
        resolver = User.query.get(rep.resolved_by_id) if rep.resolved_by_id else None

        target_preview = "N/A"
        if rep.target_type == 'chat_message':
            msg = ChatMessage.query.get(rep.target_id)
            if msg:
                target_preview = msg.content
        elif rep.target_type == 'comment':
            cmt = CourseComment.query.get(rep.target_id)
            if cmt:
                target_preview = cmt.body
        elif rep.target_type == 'opportunity':
            opp = Opportunity.query.get(rep.target_id)
            if opp:
                target_preview = f"{opp.title} at {opp.company}"

        rep_dict = rep.to_dict()
        rep_dict['reporter_username'] = reporter.username if reporter else 'Unknown'
        rep_dict['resolver_username'] = resolver.username if resolver else None
        rep_dict['target_preview'] = target_preview
        items.append(rep_dict)

    return jsonify({'reports': items}), 200

@reports_bp.route('/<int:report_id>/resolve', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def resolve_report(report_id):
    rep = Report.query.get_or_404(report_id)
    rep.resolved = True
    rep.resolved_by_id = g.current_user.id
    db.session.commit()

    log_audit('REPORT_RESOLVED', target_type='Report', target_id=report_id, notes=f"Resolved by {g.current_user.username}")
    return jsonify(rep.to_dict()), 200

@reports_bp.route('/<int:report_id>/action', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def action_report(report_id):
    rep = Report.query.get_or_404(report_id)

    action_taken = "Content Removed"
    if rep.target_type == 'chat_message':
        msg = ChatMessage.query.get(rep.target_id)
        if msg:
            msg.is_deleted = True
            msg.deleted_by_id = g.current_user.id
            msg.deleted_by_role = g.current_user.role
            action_taken = "Chat message soft-deleted"
    elif rep.target_type == 'comment':
        cmt = CourseComment.query.get(rep.target_id)
        if cmt:
            db.session.delete(cmt)
            action_taken = "Course comment deleted"
    elif rep.target_type == 'opportunity':
        opp = Opportunity.query.get(rep.target_id)
        if opp:
            opp.status = 'closed'
            action_taken = "Opportunity closed"

    rep.resolved = True
    rep.resolved_by_id = g.current_user.id
    db.session.commit()

    log_audit('REPORT_ACTION_TAKEN', target_type='Report', target_id=report_id, notes=action_taken)
    return jsonify({'message': f"Report action completed: {action_taken}", 'report': rep.to_dict()}), 200
