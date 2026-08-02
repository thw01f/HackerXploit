import hashlib
from flask import request
from flask_socketio import emit, join_room, leave_room
from app import socketio, db
from app.models import ChatMessage, User, DeviceSession, SiteFeatureToggle

online_users = set()
# Per-connection auth state, resolved once from the session cookie at connect time
# so the client never needs to hold or transmit the raw session token itself.
sid_to_user = {}

def _authenticate_socket():
    token = request.cookies.get('session_token')
    if not token:
        return None
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    sess = DeviceSession.query.filter_by(session_token_hash=token_hash, is_active=True).first()
    if not sess:
        return None
    user = User.query.get(sess.user_id)
    if not user or user.status != 'approved':
        return None
    return user

@socketio.on('connect')
def handle_connect():
    user = _authenticate_socket()
    if not user:
        return False  # Reject the connection outright
    sid_to_user[request.sid] = user.id
    online_users.add(user.id)
    join_room(f"user_{user.id}")
    emit('presence_update', {'online_count': len(online_users)}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    user_id = sid_to_user.pop(request.sid, None)
    if user_id is not None and user_id not in sid_to_user.values():
        online_users.discard(user_id)
    emit('presence_update', {'online_count': len(online_users)}, broadcast=True)

@socketio.on('join_channel')
def handle_join(data):
    channel = data.get('channel', 'general')
    join_room(channel)
    emit('status', {'msg': f'Joined {channel}'}, room=channel)

@socketio.on('send_message')
def handle_send_message(data):
    channel = data.get('channel', 'general')
    content = data.get('content', '').strip()

    if not content:
        return

    # Check site feature toggle for general chat
    if channel == 'general':
        toggle = SiteFeatureToggle.query.first()
        if toggle and not toggle.general_chat_enabled:
            emit('error', {'message': 'General chat is currently disabled by admin'}, room=request.sid)
            return

    user_id = sid_to_user.get(request.sid)
    user = User.query.get(user_id) if user_id else None
    if not user or user.status != 'approved':
        return

    # Create text message
    msg = ChatMessage(
        channel=channel,
        user_id=user.id,
        content=content
    )
    db.session.add(msg)
    db.session.commit()

    payload = msg.to_dict()
    payload['sender_username'] = user.username
    payload['sender_avatar'] = user.avatar_url
    payload['sender_role'] = user.role

    emit('new_message', payload, room=channel)

def emit_user_notification(user_id, notification_dict):
    """Utility function to broadcast real-time notification to specific user room"""
    socketio.emit('new_notification', notification_dict, room=f"user_{user_id}")
