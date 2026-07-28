from datetime import datetime
from flask import Blueprint, request, jsonify, g
from app.models import db, Opportunity, OpportunityApplication, Skill, member_skills, opportunity_skills, User
from app.utils.decorators import require_auth, require_role, log_audit

opportunity_bp = Blueprint('opportunity', __name__, url_prefix='/api/opportunities')

@opportunity_bp.route('', methods=['GET'])
@require_auth
def get_opportunities():
    type_filter = request.args.get('type')
    include_expired = request.args.get('include_expired', 'false').lower() == 'true'

    query = Opportunity.query

    if type_filter and type_filter != 'all':
        query = query.filter_by(type=type_filter)

    if not include_expired:
        now = datetime.utcnow()
        query = query.filter((Opportunity.deadline == None) | (Opportunity.deadline >= now))

    opportunities = query.all()

    # Get current user's skill IDs
    user_skill_rows = db.session.query(member_skills.c.skill_id).filter_by(user_id=g.current_user.id).all()
    user_skill_ids = {r[0] for r in user_skill_rows}

    results = []
    for opp in opportunities:
        opp_dict = opp.to_dict()
        opp_skill_ids = {s['id'] for s in opp_dict['skills']}

        # Simple set intersection
        matched_count = len(user_skill_ids.intersection(opp_skill_ids))
        opp_dict['matched_skills_count'] = matched_count
        opp_dict['total_skills_count'] = len(opp_skill_ids)

        results.append(opp_dict)

    # Sort soonest deadline first (opportunities without deadline go last)
    def deadline_key(o):
        return o['deadline'] or '9999-12-31'

    results.sort(key=deadline_key)

    return jsonify({'opportunities': results}), 200

@opportunity_bp.route('', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def create_opportunity():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    company = data.get('company') or data.get('organization', '').strip()
    desc = data.get('description', '')

    if not title or not company or not desc:
        return jsonify({'error': 'Title, company, and description are required'}), 400

    deadline = datetime.fromisoformat(data['deadline']) if data.get('deadline') else None

    opp = Opportunity(
        title=title,
        company=company,
        type=data.get('type', 'internship'),
        description=desc,
        apply_link=data.get('apply_link'),
        location=data.get('location', 'Remote'),
        deadline=deadline,
        posted_by_id=g.current_user.id,
        status='open'
    )

    # Attach skills if provided
    skill_ids = data.get('skill_ids', [])
    if skill_ids:
        skills = Skill.query.filter(Skill.id.in_(skill_ids)).all()
        opp.skills.extend(skills)

    db.session.add(opp)
    db.session.commit()

    log_audit('OPPORTUNITY_CREATE', target_type='Opportunity', target_id=opp.id, details={'title': title})
    return jsonify(opp.to_dict()), 201

# Master Skills API
@opportunity_bp.route('/skills', methods=['GET'])
@require_auth
def get_master_skills():
    skills = Skill.query.order_by(Skill.name.asc()).all()
    return jsonify({'skills': [s.to_dict() for s in skills]}), 200

@opportunity_bp.route('/skills', methods=['POST'])
@require_role('admin', 'root_admin')
def create_master_skill():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Skill name required'}), 400

    existing = Skill.query.filter(Skill.name.ilike(name)).first()
    if existing:
        return jsonify(existing.to_dict()), 200

    skill = Skill(name=name)
    db.session.add(skill)
    db.session.commit()

    log_audit('SKILL_CREATE', target_type='Skill', target_id=skill.id, details={'name': name})
    return jsonify(skill.to_dict()), 201

# User Skills Profile API
@opportunity_bp.route('/user/skills', methods=['GET'])
@require_auth
def get_user_skills():
    rows = db.session.query(Skill).join(member_skills).filter(member_skills.c.user_id == g.current_user.id).all()
    return jsonify({'skills': [s.to_dict() for s in rows]}), 200

@opportunity_bp.route('/user/skills', methods=['POST'])
@require_auth
def set_user_skills():
    data = request.get_json() or {}
    skill_ids = data.get('skill_ids', [])

    # Delete existing member skills for this user
    db.session.execute(member_skills.delete().where(member_skills.c.user_id == g.current_user.id))

    if skill_ids:
        for sid in skill_ids:
            db.session.execute(member_skills.insert().values(user_id=g.current_user.id, skill_id=sid))

    db.session.commit()
    return jsonify({'message': 'Skills updated successfully'}), 200
