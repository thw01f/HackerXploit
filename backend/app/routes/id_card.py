import secrets
from datetime import datetime
from flask import Blueprint, request, jsonify, g, Response
from app.models import db, User, IDCardToken, CompetitionParticipation, Competition
from app.utils.decorators import require_auth, log_audit
from app.services.qr_service import generate_branded_qr_png

id_card_bp = Blueprint('id_card', __name__, url_prefix='/api')

def get_or_create_active_token(user_id):
    active_token = IDCardToken.query.filter_by(user_id=user_id, revoked_at=None).first()
    if not active_token:
        token_str = secrets.token_hex(32) # 64-character random hex token
        active_token = IDCardToken(user_id=user_id, token=token_str)
        db.session.add(active_token)
        db.session.commit()
    return active_token

@id_card_bp.route('/profile/id-card', methods=['GET'])
@require_auth
def get_user_id_card():
    user = g.current_user
    token_obj = get_or_create_active_token(user.id)

    # Calculate live participation status
    now = datetime.utcnow()
    active_part = db.session.query(CompetitionParticipation, Competition).join(
        Competition, CompetitionParticipation.competition_id == Competition.id
    ).filter(
        CompetitionParticipation.user_id == user.id,
        CompetitionParticipation.application_status == 'verified',
        Competition.starts_at <= now,
        Competition.ends_at >= now
    ).first()

    is_active_event = active_part is not None
    active_event_name = active_part[1].title if active_part else None

    user_dict = user.to_dict(include_private=False)
    user_dict['member_id'] = user.get_badge_id()

    return jsonify({
        'user': user_dict,
        'token': token_obj.token,
        'verification_url': f"https://club.hackerxploit.org/verify/{token_obj.token}",
        'live_status': {
            'is_active_event': is_active_event,
            'active_event_name': active_event_name
        }
    }), 200

@id_card_bp.route('/profile/id-card/qr.png', methods=['GET'])
@require_auth
def get_user_id_card_qr():
    """Server-rendered branded QR (HackerXploit logo embedded) for the
    current user's verification URL - replaces the old client-side approach
    of loading a QR-drawing script from a public CDN at runtime."""
    user = g.current_user
    token_obj = get_or_create_active_token(user.id)
    verification_url = f"https://club.hackerxploit.org/verify/{token_obj.token}"
    png_bytes = generate_branded_qr_png(verification_url)
    return Response(png_bytes, mimetype='image/png', headers={
        'Cache-Control': 'no-store, must-revalidate',
        'Pragma': 'no-cache'
    })

@id_card_bp.route('/profile/id-card/regenerate', methods=['POST'])
@require_auth
def regenerate_id_card_token():
    user = g.current_user
    existing_tokens = IDCardToken.query.filter_by(user_id=user.id, revoked_at=None).all()
    now = datetime.utcnow()
    for t in existing_tokens:
        t.revoked_at = now

    new_token_str = secrets.token_hex(32)
    new_token = IDCardToken(user_id=user.id, token=new_token_str)
    db.session.add(new_token)
    db.session.commit()

    log_audit('ID_CARD_TOKEN_REGENERATED', target_type='IDCardToken', target_id=new_token.id)
    return jsonify({
        'message': 'Virtual ID Card verification token regenerated successfully',
        'token': new_token.token,
        'verification_url': f"https://club.hackerxploit.org/verify/{new_token.token}"
    }), 200

@id_card_bp.route('/verify/<token>', methods=['GET'])
def verify_id_card_token(token):
    token_obj = IDCardToken.query.filter_by(token=token, revoked_at=None).first()
    if not token_obj:
        return jsonify({'error': 'Invalid or revoked ID card verification token'}), 404

    user = User.query.get(token_obj.user_id)
    if not user or user.status != 'approved':
        return jsonify({'error': 'Member account is inactive or suspended'}), 404

    # Calculate live participation status
    now = datetime.utcnow()
    active_part = db.session.query(CompetitionParticipation, Competition).join(
        Competition, CompetitionParticipation.competition_id == Competition.id
    ).filter(
        CompetitionParticipation.user_id == user.id,
        CompetitionParticipation.application_status == 'verified',
        Competition.starts_at <= now,
        Competition.ends_at >= now
    ).first()

    is_active_event = active_part is not None
    active_event_name = active_part[1].title if active_part else None

    return jsonify({
        'status': 'verified',
        'member': {
            'username': user.username,
            'full_name': user.full_name or user.username,
            'member_id': user.get_badge_id(),
            'registration_number': user.registration_number,
            'role': user.role,
            'specialization_role': user.specialization_role,
            'department': user.department,
            'academic_year': user.academic_year,
            'member_since': user.created_at.strftime('%B %Y'),
            'avatar_url': getattr(user, 'avatar_url', None)
        },
        'live_status': {
            'is_actively_participating': is_active_event,
            'active_event_name': active_event_name
        },
        'verified_at': datetime.utcnow().isoformat()
    }), 200
