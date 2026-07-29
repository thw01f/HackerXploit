from flask import Blueprint, request, jsonify, g
from app.models import db, Notification
from app.utils.decorators import require_auth

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@notifications_bp.route('', methods=['GET'])
@require_auth
def get_notifications():
    notes = Notification.query.filter_by(user_id=g.current_user.id).order_by(Notification.created_at.desc()).limit(50).all()
    unread_count = Notification.query.filter_by(user_id=g.current_user.id, is_read=False).count()
    return jsonify({
        'notifications': [n.to_dict() for n in notes],
        'unread_count': unread_count
    }), 200

@notifications_bp.route('/<int:note_id>/read', methods=['PUT'])
@require_auth
def mark_notification_read(note_id):
    note = Notification.query.filter_by(id=note_id, user_id=g.current_user.id).first_or_404()
    note.is_read = True
    db.session.commit()
    return jsonify(note.to_dict()), 200

@notifications_bp.route('/read-all', methods=['POST'])
@require_auth
def mark_all_notifications_read():
    notes = Notification.query.filter_by(user_id=g.current_user.id, is_read=False).all()
    for n in notes:
        n.is_read = True
    db.session.commit()
    return jsonify({'message': 'All notifications marked as read'}), 200
