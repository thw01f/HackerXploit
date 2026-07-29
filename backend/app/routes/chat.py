from datetime import datetime
from flask import Blueprint, request, jsonify, g
from app.models import db, ChatMessage, Notification, User, SiteFeatureToggle, Report
from app.utils.decorators import require_auth, require_role, log_audit
from app import limiter


chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

@chat_bp.route('/messages', methods=['GET'])
@require_auth
def get_messages():
    channel = request.args.get('channel', 'general')
    limit = int(request.args.get('limit', 50))
    messages = ChatMessage.query.filter_by(channel=channel)\
        .order_by(ChatMessage.timestamp.desc())\
        .limit(limit).all()

    messages.reverse()

    # Check if general chat toggle is active
    toggle = SiteFeatureToggle.query.first()
    chat_enabled = toggle.general_chat_enabled if toggle else True

    res = []
    for m in messages:
        sender = User.query.get(m.user_id)
        msg_dict = m.to_dict()
        msg_dict['sender_username'] = sender.username if sender else 'Unknown'
        msg_dict['sender_avatar'] = sender.avatar_url if sender else None
        msg_dict['sender_role'] = sender.role if sender else 'member'
        res.append(msg_dict)

    return jsonify({
        'messages': res,
        'chat_enabled': chat_enabled
    }), 200

@chat_bp.route('/messages', methods=['POST'])
@require_auth
@limiter.limit("30 per minute")
def post_message():
    channel = request.json.get('channel', 'general')
    content = request.json.get('content', '').strip()

    if not content:
        return jsonify({'error': 'Message content cannot be empty'}), 400

    # Enforce text-only check & admin toggle
    if channel == 'general':
        toggle = SiteFeatureToggle.query.first()
        if toggle and not toggle.general_chat_enabled:
            return jsonify({'error': 'General chat is currently disabled by admin'}), 403

    msg = ChatMessage(
        channel=channel,
        user_id=g.current_user.id,
        content=content
    )
    db.session.add(msg)
    db.session.commit()

    payload = msg.to_dict()
    payload['sender_username'] = g.current_user.username
    payload['sender_avatar'] = g.current_user.avatar_url
    payload['sender_role'] = g.current_user.role

    try:
        from app import socketio
        socketio.emit('new_message', payload, room=channel)
    except Exception as e:
        pass

    return jsonify(payload), 201

@chat_bp.route('/messages/<int:message_id>', methods=['DELETE'])
@require_role('teacher', 'admin', 'root_admin')
def soft_delete_message(message_id):
    msg = ChatMessage.query.get_or_404(message_id)
    msg.is_deleted = True
    msg.deleted_by_id = g.current_user.id
    msg.deleted_by_role = g.current_user.role
    msg.deleted_at = datetime.utcnow()
    db.session.commit()

    log_audit('CHAT_SOFT_DELETE', target_type='ChatMessage', target_id=message_id, notes=f"Deleted by {g.current_user.username} ({g.current_user.role})")
    return jsonify({'message': 'Message soft-deleted', 'chat_message': msg.to_dict()}), 200

@chat_bp.route('/reset', methods=['POST'])
@require_role('admin')
def reset_chat_room():
    """ONLY Admin can hard-reset the entire chat room"""
    channel = request.json.get('channel', 'general')
    count = ChatMessage.query.filter_by(channel=channel).delete()
    db.session.commit()

    log_audit('CHAT_HARD_RESET', notes=f"Hard-reset channel '{channel}' deleting {count} messages")
    return jsonify({'message': f"Chat room '{channel}' reset successfully. {count} messages purged."}), 200

@chat_bp.route('/messages/<int:message_id>/report', methods=['POST'])
@require_auth
def report_chat_message(message_id):
    reason = request.json.get('reason', '').strip()
    if not reason:
        return jsonify({'error': 'Report reason is required'}), 400

    msg = ChatMessage.query.get_or_404(message_id)
    rep = Report(
        reported_by_id=g.current_user.id,
        target_type='chat_message',
        target_id=message_id,
        reason=reason
    )
    db.session.add(rep)
    db.session.commit()

    log_audit('CHAT_MESSAGE_REPORTED', target_type='ChatMessage', target_id=message_id, notes=reason)
    return jsonify({'message': 'Chat message reported for moderation', 'report': rep.to_dict()}), 201
