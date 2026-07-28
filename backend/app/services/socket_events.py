from flask import request
from flask_socketio import emit, join_room, leave_room
from app import socketio, db
from app.models import ChatMessage, User, DeviceSession

online_users = set()

@socketio.on('connect')
def handle_connect():
    token = request.args.get('token')
    if token:
        sess = DeviceSession.query.filter_by(session_token=token, is_active=True).first()
        if sess:
            online_users.add(sess.user_id)
            emit('presence_update', {'online_count': len(online_users)}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    # Presence update broadcast
    emit('presence_update', {'online_count': len(online_users)}, broadcast=True)

@socketio.on('join_channel')
def handle_join(data):
    channel = data.get('channel', 'general')
    join_room(channel)
    emit('status', {'msg': f'Joined {channel}'}, room=channel)

@socketio.on('send_message')
def handle_send_message(data):
    token = data.get('token')
    channel = data.get('channel', 'general')
    content = data.get('content', '').strip()

    if not content or not token:
        return

    sess = DeviceSession.query.filter_by(session_token=token, is_active=True).first()
    if not sess:
        return

    user = User.query.get(sess.user_id)
    if not user or user.status != 'approved':
        return

    # Create message
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
