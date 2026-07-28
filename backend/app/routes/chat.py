from flask import Blueprint, request, jsonify, g
from app.models import db, ChatMessage, Notification, User
from app.utils.decorators import require_auth, require_role, log_audit

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

@chat_bp.route('/messages', methods=['GET'])
@require_auth
def get_messages():
    channel = request.args.get('channel', 'general')
    limit = int(request.args.get('limit', 50))
    messages = ChatMessage.query.filter_by(channel=channel)\
        .order_by(ChatMessage.timestamp.asc())\
        .limit(limit).all()

    # Attach sender info
    res = []
    for m in messages:
        sender = User.query.get(m.user_id)
        msg_dict = m.to_dict()
        msg_dict['sender_username'] = sender.username if sender else 'Unknown'
        msg_dict['sender_avatar'] = sender.avatar_url if sender else None
        msg_dict['sender_role'] = sender.role if sender else 'member'
        res.append(msg_dict)

    return jsonify({'messages': res}), 200

@chat_bp.route('/messages/<int:message_id>', methods=['DELETE'])
@require_role('teacher', 'admin', 'root_admin')
def soft_delete_message(message_id):
    msg = ChatMessage.query.get_or_404(message_id)
    msg.is_deleted = True
    msg.deleted_by_id = g.current_user.id
    db.session.commit()

    log_audit('CHAT_SOFT_DELETE', target_type='ChatMessage', target_id=message_id)
    return jsonify({'message': 'Message soft-deleted', 'chat_message': msg.to_dict()}), 200

@chat_bp.route('/notifications', methods=['GET'])
@require_auth
def get_notifications():
    notes = Notification.query.filter_by(user_id=g.current_user.id).order_by(Notification.created_at.desc()).limit(20).all()
    return jsonify({'notifications': [n.to_dict() for n in notes]}), 200
