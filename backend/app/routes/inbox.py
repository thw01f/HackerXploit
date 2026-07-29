from datetime import datetime
from flask import Blueprint, request, jsonify, g
from app.models import db, Message, MessageRecipient, User, Notification
from app.utils.decorators import require_auth, require_role, log_audit
from app.services.socket_events import emit_user_notification
from app.services.email_service import send_offline_inbox_email
from app.routes.activity import get_redis

inbox_bp = Blueprint('inbox', __name__, url_prefix='/api/inbox')


@inbox_bp.route('/messages', methods=['POST'])
@require_auth
def compose_message():
    data = request.get_json() or {}
    subject = data.get('subject', '').strip()
    body = data.get('body', '').strip()
    scope = data.get('scope', 'individual')
    allow_reply = data.get('allow_reply', True)
    target_user_ids = data.get('target_user_ids', [])
    if isinstance(target_user_ids, (int, str)):
        try:
            target_user_ids = [int(target_user_ids)]
        except ValueError:
            target_user_ids = []
    elif isinstance(target_user_ids, list):
        target_user_ids = [int(x) for x in target_user_ids if str(x).isdigit()]

    if not subject or not body:
        return jsonify({'error': 'Subject and body are required'}), 400

    # Restrict broadcast scopes & member recipient rules
    broadcast_scopes = ('all_members', 'role:teacher', 'role:member', 'role:admin')
    if scope in broadcast_scopes and g.current_user.role not in ('teacher', 'admin', 'root_admin'):
        return jsonify({'error': 'Broadcast messages are reserved for Teachers and Admins.'}), 403

    # Members can only message Teachers and Admins
    if g.current_user.role == 'member':
        if scope not in ('individual', 'custom_list'):
            return jsonify({'error': 'Members can only send direct messages to Teachers and Admins.'}), 403
        if target_user_ids:
            target_users = User.query.filter(User.id.in_(target_user_ids)).all()
            invalid_targets = [u for u in target_users if u.role not in ('teacher', 'admin', 'root_admin')]
            if invalid_targets:
                return jsonify({'error': 'Members can only send direct messages to Teachers and Admins, not to other members.'}), 403

    # Resolve target user IDs based on scope
    recipients = []
    if scope == 'all_members':
        recipients = User.query.filter_by(status='approved').all()
    elif scope.startswith('role:'):
        target_role = scope.split('role:')[1]
        recipients = User.query.filter_by(role=target_role, status='approved').all()
    elif scope in ('individual', 'custom_list'):
        if target_user_ids:
            recipients = User.query.filter(User.id.in_(target_user_ids), User.status == 'approved').all()

    if not recipients:
        return jsonify({'error': 'No valid recipient users selected'}), 400

    # Create master message
    msg = Message(
        sender_id=g.current_user.id,
        subject=subject,
        body=body,
        scope=scope,
        allow_reply=allow_reply,
        sent_at=datetime.utcnow()
    )
    db.session.add(msg)
    db.session.commit()

    # Create recipients & in-app notifications
    for u in recipients:
        mr = MessageRecipient(message_id=msg.id, user_id=u.id)
        db.session.add(mr)

        # In-app notification
        notif = Notification(
            user_id=u.id,
            type='inbox',
            title=f"New Message: {subject}",
            message=body[:120] + ('...' if len(body) > 120 else ''),
            link=f"/inbox?msg={msg.id}"
        )
        db.session.add(notif)
        db.session.commit()

        # SocketIO live broadcast
        emit_user_notification(u.id, notif.to_dict())

        # Check offline status in Redis
        is_online = False
        r = get_redis()
        if r:
            try:
                val = r.get(f"online:{u.id}")
                if val:
                    is_online = True
            except Exception:
                pass


        if not is_online:
            snippet = body[:200] + ('...' if len(body) > 200 else '')
            from flask import current_app
            if current_app.config.get('TESTING'):
                try:
                    send_offline_inbox_email(u.id, subject, snippet)
                except Exception:
                    pass
            else:
                try:
                    send_offline_inbox_email.delay(u.id, subject, snippet)
                except Exception:
                    pass



    log_audit('MESSAGE_SENT', target_type='Message', target_id=msg.id, notes=f"Scope: {scope}, Recipients: {len(recipients)}")
    return jsonify({'message': 'Message sent successfully', 'data': msg.to_dict(), 'recipient_count': len(recipients)}), 201

@inbox_bp.route('', methods=['GET'])
@require_auth
def get_inbox():
    recipients = MessageRecipient.query.filter_by(
        user_id=g.current_user.id,
        is_deleted_by_recipient=False
    ).all()

    items = []
    for r in recipients:
        msg = Message.query.get(r.message_id)
        if not msg:
            continue
        sender = User.query.get(msg.sender_id)
        items.append({
            'recipient_id': r.id,
            'message_id': msg.id,
            'subject': msg.subject,
            'body': msg.body,
            'scope': msg.scope,
            'allow_reply': msg.allow_reply,
            'sent_at': msg.sent_at.isoformat() if msg.sent_at else None,
            'is_read': r.is_read,
            'read_at': r.read_at.isoformat() if r.read_at else None,
            'is_archived': r.is_archived,
            'sender_id': msg.sender_id,
            'sender_name': sender.full_name or sender.username if sender else 'Unknown',
            'sender_username': sender.username if sender else 'Unknown',
            'sender_role': sender.role if sender else 'member'
        })

    items.sort(key=lambda x: x['sent_at'] or '', reverse=True)
    unread_count = sum(1 for i in items if not i['is_read'])

    return jsonify({'inbox': items, 'unread_count': unread_count}), 200

@inbox_bp.route('/sent', methods=['GET'])
@require_auth
def get_sent():
    messages = Message.query.filter_by(sender_id=g.current_user.id).order_by(Message.sent_at.desc()).all()
    res = []
    for msg in messages:
        recipients = MessageRecipient.query.filter_by(message_id=msg.id).all()
        read_count = sum(1 for r in recipients if r.is_read)
        total_count = len(recipients)
        msg_dict = msg.to_dict()
        msg_dict['read_count'] = read_count
        msg_dict['total_recipients'] = total_count
        res.append(msg_dict)

    return jsonify({'sent': res}), 200

@inbox_bp.route('/<int:message_id>', methods=['GET'])
@require_auth
def get_message_detail(message_id):
    msg = Message.query.get_or_404(message_id)

    # Authorization check
    is_sender = (msg.sender_id == g.current_user.id)
    rec_entry = MessageRecipient.query.filter_by(message_id=message_id, user_id=g.current_user.id).first()

    if not is_sender and not rec_entry and g.current_user.role not in ('admin', 'root_admin'):
        return jsonify({'error': 'Unauthorized to view this message'}), 403

    # If recipient views, mark read
    if rec_entry and not rec_entry.is_read:
        rec_entry.is_read = True
        rec_entry.read_at = datetime.utcnow()
        db.session.commit()

    sender = User.query.get(msg.sender_id)
    msg_dict = msg.to_dict()
    msg_dict['sender_name'] = sender.full_name or sender.username if sender else 'Unknown'
    msg_dict['sender_username'] = sender.username if sender else 'Unknown'
    msg_dict['sender_role'] = sender.role if sender else 'member'

    return jsonify({'message': msg_dict}), 200

@inbox_bp.route('/<int:message_id>/reply', methods=['POST'])
@require_auth
def reply_message(message_id):
    parent_msg = Message.query.get_or_404(message_id)

    if not parent_msg.allow_reply:
        return jsonify({'error': 'Sender disabled replies for this message'}), 403

    body = request.json.get('body', '').strip()
    if not body:
        return jsonify({'error': 'Reply body is required'}), 400

    reply_subject = f"Re: {parent_msg.subject}"
    reply_msg = Message(
        sender_id=g.current_user.id,
        subject=reply_subject,
        body=body,
        scope='individual',
        allow_reply=True,
        sent_at=datetime.utcnow()
    )
    db.session.add(reply_msg)
    db.session.commit()

    # Add original sender as recipient
    mr = MessageRecipient(message_id=reply_msg.id, user_id=parent_msg.sender_id)
    db.session.add(mr)

    # In-app notification
    notif = Notification(
        user_id=parent_msg.sender_id,
        type='inbox',
        title=f"Reply: {parent_msg.subject}",
        message=body[:120] + ('...' if len(body) > 120 else ''),
        link=f"/inbox?msg={reply_msg.id}"
    )
    db.session.add(notif)
    db.session.commit()

    emit_user_notification(parent_msg.sender_id, notif.to_dict())

    return jsonify({'message': 'Reply sent successfully', 'reply': reply_msg.to_dict()}), 201

@inbox_bp.route('/recipients/<int:recipient_id>/read', methods=['PUT'])
@require_auth
def mark_recipient_read(recipient_id):
    r = MessageRecipient.query.filter_by(id=recipient_id, user_id=g.current_user.id).first_or_404()
    r.is_read = True
    r.read_at = datetime.utcnow()
    db.session.commit()
    return jsonify(r.to_dict()), 200

@inbox_bp.route('/recipients/<int:recipient_id>/archive', methods=['PUT'])
@require_auth
def archive_recipient_message(recipient_id):
    r = MessageRecipient.query.filter_by(id=recipient_id, user_id=g.current_user.id).first_or_404()
    r.is_archived = not r.is_archived
    db.session.commit()
    return jsonify(r.to_dict()), 200

@inbox_bp.route('/recipients/<int:recipient_id>', methods=['DELETE'])
@require_auth
def delete_recipient_message(recipient_id):
    """Delete message from my inbox (recipient copy only, sender's copy untouched)"""
    r = MessageRecipient.query.filter_by(id=recipient_id, user_id=g.current_user.id).first_or_404()
    r.is_deleted_by_recipient = True
    db.session.commit()
    return jsonify({'message': 'Message removed from your inbox'}), 200

@inbox_bp.route('/users', methods=['GET'])
@require_auth
def get_inbox_user_directory():
    """Returns directory of approved platform users for direct messaging. Members can only message Teachers & Admins."""
    query = User.query.filter(User.status == 'approved', User.id != g.current_user.id)
    if g.current_user.role == 'member':
        query = query.filter(User.role.in_(['teacher', 'admin', 'root_admin']))
    users = query.order_by(User.role.asc(), User.username.asc()).all()
    res = []
    for u in users:
        res.append({
            'id': u.id,
            'username': u.username,
            'full_name': u.full_name or u.username,
            'role': u.role,
            'specialization_role': getattr(u, 'specialization_role', None),
            'avatar_url': getattr(u, 'avatar_url', None)
        })
    return jsonify({'users': res}), 200

@inbox_bp.route('/admin/log', methods=['GET'])
@require_role('admin')
def get_admin_inbox_log():
    """Site-wide broadcast & direct message sent audit log with read-rates for admin oversight"""
    messages = Message.query.order_by(Message.sent_at.desc()).all()
    res = []
    for msg in messages:
        sender = User.query.get(msg.sender_id)
        recipients = MessageRecipient.query.filter_by(message_id=msg.id).all()
        total_recipients = len(recipients)
        read_count = sum(1 for r in recipients if r.is_read)
        read_rate_pct = round((read_count / total_recipients * 100), 1) if total_recipients > 0 else 0.0

        res.append({
            'message_id': msg.id,
            'sender_id': msg.sender_id,
            'sender_username': sender.username if sender else 'Unknown',
            'sender_role': sender.role if sender else 'member',
            'subject': msg.subject,
            'body': msg.body,
            'scope': msg.scope,
            'sent_at': msg.sent_at.isoformat() if msg.sent_at else None,
            'total_recipients': total_recipients,
            'read_count': read_count,
            'read_rate_pct': read_rate_pct,
            'allow_reply': msg.allow_reply
        })

    return jsonify({'inbox_logs': res}), 200
