from datetime import datetime
from flask import Blueprint, request, jsonify, g
from app.models import db, Opportunity, OpportunityApplication
from app.utils.decorators import require_auth, require_role, log_audit

opportunity_bp = Blueprint('opportunity', __name__, url_prefix='/api/opportunities')

@opportunity_bp.route('', methods=['GET'])
@require_auth
def get_opportunities():
    opps = Opportunity.query.order_by(Opportunity.created_at.desc()).all()
    return jsonify({'opportunities': [o.to_dict() for o in opps]}), 200

@opportunity_bp.route('', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def create_opportunity():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    org = data.get('organization', '').strip()
    desc = data.get('description', '')

    if not title or not org or not desc:
        return jsonify({'error': 'Title, Organization, and Description required'}), 400

    deadline = datetime.fromisoformat(data['deadline']) if data.get('deadline') else None

    opp = Opportunity(
        title=title,
        organization=org,
        type=data.get('type', 'Internship'),
        description=desc,
        location=data.get('location', 'Remote'),
        deadline=deadline,
        posted_by_id=g.current_user.id
    )
    db.session.add(opp)
    db.session.commit()

    log_audit('OPPORTUNITY_CREATE', target_type='Opportunity', target_id=opp.id, details={'title': title})
    return jsonify(opp.to_dict()), 201

@opportunity_bp.route('/<int:opp_id>/apply', methods=['POST'])
@require_auth
def apply_opportunity(opp_id):
    opp = Opportunity.query.get_or_404(opp_id)
    data = request.get_json() or {}

    app_record = OpportunityApplication(
        opportunity_id=opp_id,
        user_id=g.current_user.id,
        resume_url=data.get('resume_url'),
        cover_letter=data.get('cover_letter', '')
    )
    db.session.add(app_record)
    db.session.commit()

    log_audit('OPPORTUNITY_APPLY', target_type='OpportunityApplication', target_id=app_record.id)
    return jsonify(app_record.to_dict()), 201
