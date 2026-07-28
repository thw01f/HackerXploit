from datetime import datetime
from flask import Blueprint, request, jsonify, g
from app.models import db, Competition, CompetitionParticipation, User, Certificate
from app.utils.decorators import require_auth, require_role, log_audit
from app.services.pdf_service import generate_completion_certificate

competition_bp = Blueprint('competition', __name__, url_prefix='/api/competitions')

@competition_bp.route('', methods=['GET'])
@require_auth
def get_competitions():
    category = request.args.get('category', 'All')
    status_filter = request.args.get('status', 'all')
    priority_filter = request.args.get('priority', 'all')
    involvement_filter = request.args.get('involvement', 'all')

    query = Competition.query.filter_by(is_archived=False)

    if category and category != 'All':
        query = query.filter(Competition.category.ilike(category))

    if status_filter and status_filter != 'all':
        query = query.filter_by(status=status_filter)

    if priority_filter and priority_filter != 'all':
        query = query.filter_by(priority=priority_filter)

    competitions = query.all()

    # User involvement mapping for current user
    user_participations = {
        p.competition_id: p for p in CompetitionParticipation.query.filter_by(user_id=g.current_user.id).all()
    }

    results = []
    for c in competitions:
        p = user_participations.get(c.id)
        user_involvement = 'not_applied'
        if p:
            user_involvement = p.application_status  # pending_verification, verified, rejected

        if involvement_filter != 'all':
            if involvement_filter == 'applied' and user_involvement == 'not_applied':
                continue
            if involvement_filter == 'verified' and user_involvement != 'verified':
                continue
            if involvement_filter == 'not_applied' and user_involvement != 'not_applied':
                continue

        c_dict = c.to_dict()
        c_dict['user_involvement'] = user_involvement
        c_dict['user_participation'] = p.to_dict() if p else None
        results.append(c_dict)

    # Sort priority-first (high=0, medium=1, normal=2) then soonest deadline
    priority_map = {'high': 0, 'medium': 1, 'normal': 2}
    
    def sort_key(item):
        p_val = priority_map.get(item['priority'], 2)
        deadline = item['application_deadline'] or item['starts_at'] or '9999-12-31'
        return (p_val, deadline)

    results.sort(key=sort_key)

    return jsonify({'competitions': results}), 200

@competition_bp.route('', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def announce_competition():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    description = data.get('description', '')
    starts_at_str = data.get('starts_at') or data.get('start_date')
    ends_at_str = data.get('ends_at') or data.get('end_date')

    if not title or not starts_at_str or not ends_at_str:
        return jsonify({'error': 'Title, starts_at, and ends_at dates are required'}), 400

    starts_at = datetime.fromisoformat(starts_at_str)
    ends_at = datetime.fromisoformat(ends_at_str)
    deadline = datetime.fromisoformat(data['application_deadline']) if data.get('application_deadline') else None

    # Compute status based on current time
    now = datetime.utcnow()
    if now < starts_at:
        status = 'upcoming'
    elif starts_at <= now <= ends_at:
        status = 'ongoing'
    else:
        status = 'ended'

    comp = Competition(
        title=title,
        description=description,
        poster_image=data.get('poster_image'),
        external_link=data.get('external_link'),
        starts_at=starts_at,
        ends_at=ends_at,
        application_deadline=deadline,
        category=data.get('category', 'ctf'),
        priority=data.get('priority', 'normal'),
        posted_by_id=g.current_user.id,
        status=status
    )
    db.session.add(comp)
    db.session.commit()

    log_audit('COMPETITION_ANNOUNCE', target_type='Competition', target_id=comp.id, details={'title': title})
    return jsonify(comp.to_dict()), 201

@competition_bp.route('/<int:comp_id>/apply', methods=['POST'])
@require_auth
def apply_competition(comp_id):
    comp = Competition.query.get_or_404(comp_id)
    data = request.get_json() or {}
    screenshot_url = data.get('application_screenshot')

    if not screenshot_url:
        return jsonify({'error': 'Application registration screenshot proof is required'}), 400

    existing = CompetitionParticipation.query.filter_by(competition_id=comp_id, user_id=g.current_user.id).first()
    if existing:
        existing.application_screenshot = screenshot_url
        existing.application_status = 'pending_verification'
        existing.applied_at = datetime.utcnow()
        db.session.commit()
        return jsonify(existing.to_dict()), 200

    part = CompetitionParticipation(
        competition_id=comp_id,
        user_id=g.current_user.id,
        application_screenshot=screenshot_url,
        application_status='pending_verification',
        applied_at=datetime.utcnow()
    )
    db.session.add(part)
    db.session.commit()

    log_audit('COMPETITION_APPLY', target_type='CompetitionParticipation', target_id=part.id)
    return jsonify(part.to_dict()), 201

@competition_bp.route('/<int:comp_id>/applications', methods=['GET'])
@require_role('teacher', 'admin', 'root_admin')
def get_applications_queue(comp_id):
    comp = Competition.query.get_or_404(comp_id)
    participations = CompetitionParticipation.query.filter_by(competition_id=comp_id).all()

    queue = []
    for p in participations:
        u = User.query.get(p.user_id)
        p_dict = p.to_dict()
        p_dict['applicant_username'] = u.username if u else 'Unknown'
        p_dict['applicant_email'] = u.email if u else None
        p_dict['applicant_full_name'] = u.full_name if u else u.username
        queue.append(p_dict)

    return jsonify({'competition': comp.to_dict(), 'applications': queue}), 200

@competition_bp.route('/<int:comp_id>/applications/<int:app_id>/verify', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def verify_application(comp_id, app_id):
    part = CompetitionParticipation.query.get_or_404(app_id)
    data = request.get_json() or {}
    status = data.get('status', 'verified')  # verified or rejected

    part.application_status = status
    part.verified_by_id = g.current_user.id
    part.verified_at = datetime.utcnow()
    db.session.commit()

    log_audit('COMPETITION_VERIFY_APP', target_type='CompetitionParticipation', target_id=app_id, details={'status': status})
    return jsonify(part.to_dict()), 200

@competition_bp.route('/<int:comp_id>/wrapup', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def file_wrapup(comp_id):
    comp = Competition.query.get_or_404(comp_id)
    data = request.get_json() or {}

    # Participations wrap-up update list: [{ 'participation_id': 1, 'result': 'winner', 'placement_label': '1st Place', ... }]
    updates = data.get('participants', [])
    summary_notes = data.get('summary_notes', '')
    event_photos = data.get('event_photos', [])

    comp.status = 'ended'
    
    for item in updates:
        part_id = item.get('participation_id')
        part = CompetitionParticipation.query.get(part_id)
        if not part:
            continue

        result_type = item.get('result', 'participated')
        part.result = result_type
        part.placement_label = item.get('placement_label')
        part.summary_notes = item.get('summary_notes') or summary_notes
        part.event_photos = item.get('event_photos') or event_photos
        part.submitted_by_id = g.current_user.id
        part.submitted_at = datetime.utcnow()

        # If winner or runner_up, generate official platform certificate
        if result_type in ('winner', 'runner_up'):
            u = User.query.get(part.user_id)
            user_name = u.full_name or u.username if u else "Competitor"
            cert_id = f"COMP-{comp.id}-{part.user_id}"
            title_text = f"{comp.title} ({item.get('placement_label', result_type.capitalize())})"
            
            pdf_path = generate_completion_certificate(user_name, title_text, cert_id)
            part.certificate_file = pdf_path

            # Create Certificate table row
            cert = Certificate(
                user_id=part.user_id,
                type='competition',
                source_id=comp.id,
                file_path=pdf_path
            )
            db.session.add(cert)

    db.session.commit()

    log_audit('COMPETITION_WRAPUP', target_type='Competition', target_id=comp.id)
    return jsonify(comp.to_dict()), 200
