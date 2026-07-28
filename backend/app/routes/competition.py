from datetime import datetime
from flask import Blueprint, request, jsonify, g
from app.models import db, Competition, CompetitionApplication
from app.utils.decorators import require_auth, require_role, log_audit

competition_bp = Blueprint('competition', __name__, url_prefix='/api/competitions')

@competition_bp.route('', methods=['GET'])
@require_auth
def get_competitions():
    if g.current_user.role in ['admin', 'root_admin']:
        comps = Competition.query.all()
    else:
        comps = Competition.query.filter(
            (Competition.status == 'approved') | (Competition.status == 'completed')
        ).all()
    return jsonify({'competitions': [c.to_dict() for c in comps]}), 200

@competition_bp.route('', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def create_competition():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    description = data.get('description', '')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')

    if not title or not start_date_str or not end_date_str:
        return jsonify({'error': 'Title, start date, and end date are required'}), 400

    start_date = datetime.fromisoformat(start_date_str)
    end_date = datetime.fromisoformat(end_date_str)

    # Admin auto-approves if creating, teacher requires admin approval
    status = 'approved' if g.current_user.role in ['admin', 'root_admin'] else 'pending_approval'

    comp = Competition(
        title=title,
        description=description,
        location=data.get('location', 'Online'),
        start_date=start_date,
        end_date=end_date,
        status=status,
        created_by_id=g.current_user.id
    )
    db.session.add(comp)
    db.session.commit()

    log_audit('COMPETITION_CREATE', target_type='Competition', target_id=comp.id, details={'title': title, 'status': status})
    return jsonify(comp.to_dict()), 201

@competition_bp.route('/<int:comp_id>/approve', methods=['POST'])
@require_role('admin', 'root_admin')
def approve_competition(comp_id):
    comp = Competition.query.get_or_404(comp_id)
    comp.status = 'approved'
    comp.approved_by_id = g.current_user.id
    db.session.commit()

    log_audit('COMPETITION_APPROVE', target_type='Competition', target_id=comp.id)
    return jsonify(comp.to_dict()), 200

@competition_bp.route('/<int:comp_id>/apply', methods=['POST'])
@require_auth
def apply_competition(comp_id):
    comp = Competition.query.get_or_404(comp_id)
    existing = CompetitionApplication.query.filter_by(competition_id=comp_id, user_id=g.current_user.id).first()
    if existing:
        return jsonify({'message': 'Already applied', 'application': existing.to_dict()}), 200

    app_record = CompetitionApplication(
        competition_id=comp_id,
        user_id=g.current_user.id,
        status='pending'
    )
    db.session.add(app_record)
    db.session.commit()

    log_audit('COMPETITION_APPLY', target_type='CompetitionApplication', target_id=app_record.id)
    return jsonify(app_record.to_dict()), 201

@competition_bp.route('/<int:comp_id>/applications/<int:app_id>/verify', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def verify_application(comp_id, app_id):
    app_record = CompetitionApplication.query.get_or_404(app_id)
    data = request.get_json() or {}
    status = data.get('status', 'verified')  # verified or rejected

    app_record.status = status
    app_record.verified_by_id = g.current_user.id
    db.session.commit()

    log_audit('COMPETITION_VERIFY_APP', target_type='CompetitionApplication', target_id=app_id, details={'status': status})
    return jsonify(app_record.to_dict()), 200

@competition_bp.route('/<int:comp_id>/wrapup', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def file_wrapup(comp_id):
    comp = Competition.query.get_or_404(comp_id)
    data = request.get_json() or {}

    comp.wrapup_notes = data.get('wrapup_notes', '')
    comp.photos = data.get('photos', [])
    comp.certificates = data.get('certificates', [])
    comp.status = 'completed'
    db.session.commit()

    log_audit('COMPETITION_WRAPUP', target_type='Competition', target_id=comp.id)
    return jsonify(comp.to_dict()), 200
