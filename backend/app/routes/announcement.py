from flask import Blueprint, request, jsonify, g
from app.models import db, Announcement
from app.utils.decorators import require_auth, require_role, log_audit

announcement_bp = Blueprint('announcement', __name__, url_prefix='/api')


@announcement_bp.route('/announcements/active', methods=['GET'])
@require_auth
def get_active_announcements():
    """Public feed for the member dashboard - active announcements only, in display order."""
    announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.display_order.asc(), Announcement.created_at.asc()).all()
    return jsonify({'announcements': [a.to_dict() for a in announcements]}), 200


@announcement_bp.route('/admin/announcements', methods=['GET'])
@require_role('admin')
def list_announcements():
    """Admin management view - every announcement, active or not."""
    announcements = Announcement.query.order_by(Announcement.display_order.asc(), Announcement.created_at.asc()).all()
    return jsonify({'announcements': [a.to_dict() for a in announcements]}), 200


@announcement_bp.route('/admin/announcements', methods=['POST'])
@require_role('admin')
def create_announcement():
    data = request.get_json() or {}
    message = (data.get('message') or '').strip()
    if not message:
        return jsonify({'error': 'Announcement message is required'}), 400

    link = (data.get('link') or '').strip() or None
    button_label = (data.get('button_label') or '').strip() or None
    if link and not button_label:
        return jsonify({'error': 'A button label is required when a link is set'}), 400

    # New announcements go to the end of the display order by default
    max_order = db.session.query(db.func.max(Announcement.display_order)).scalar() or 0

    announcement = Announcement(
        message=message,
        button_label=button_label,
        link=link,
        is_active=bool(data.get('is_active', True)),
        display_order=int(data['display_order']) if data.get('display_order') is not None else max_order + 1,
        created_by_id=g.current_user.id
    )
    db.session.add(announcement)
    db.session.commit()

    log_audit('ANNOUNCEMENT_CREATE', target_type='Announcement', target_id=announcement.id, details={'message': message})
    return jsonify(announcement.to_dict()), 201


@announcement_bp.route('/admin/announcements/<int:announcement_id>', methods=['PUT'])
@require_role('admin')
def update_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    data = request.get_json() or {}

    if 'message' in data:
        message = (data['message'] or '').strip()
        if not message:
            return jsonify({'error': 'Announcement message cannot be empty'}), 400
        announcement.message = message
    if 'button_label' in data:
        announcement.button_label = (data['button_label'] or '').strip() or None
    if 'link' in data:
        announcement.link = (data['link'] or '').strip() or None
    if announcement.link and not announcement.button_label:
        return jsonify({'error': 'A button label is required when a link is set'}), 400
    if 'is_active' in data:
        announcement.is_active = bool(data['is_active'])
    if 'display_order' in data:
        announcement.display_order = int(data['display_order'])

    db.session.commit()
    log_audit('ANNOUNCEMENT_UPDATE', target_type='Announcement', target_id=announcement.id)
    return jsonify(announcement.to_dict()), 200


@announcement_bp.route('/admin/announcements/<int:announcement_id>', methods=['DELETE'])
@require_role('admin')
def delete_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    db.session.delete(announcement)
    db.session.commit()
    log_audit('ANNOUNCEMENT_DELETE', target_type='Announcement', target_id=announcement_id)
    return jsonify({'message': 'Announcement deleted successfully'}), 200
