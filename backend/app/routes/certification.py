from flask import Blueprint, request, jsonify, g
from app.models import db, Certification, CertificationCategory, CertificationEdge
from app.utils.decorators import require_auth, require_role, log_audit

certification_bp = Blueprint('certification', __name__, url_prefix='/api/certifications')
certification_category_bp = Blueprint('certification_category', __name__, url_prefix='/api/certification-categories')

# --- Flat certification catalog (kept for consumers that just need the raw list) ---

@certification_bp.route('', methods=['GET'])
@require_auth
def get_certifications():
    if g.current_user.role in ['teacher', 'admin', 'root_admin']:
        certifications = Certification.query.order_by(Certification.created_at.desc()).all()
    else:
        certifications = Certification.query.filter_by(status='published').order_by(Certification.created_at.desc()).all()
    return jsonify({'certifications': [c.to_dict() for c in certifications]}), 200

@certification_bp.route('', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def create_certification():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Certification title is required'}), 400

    certification = Certification(
        category_id=data.get('category_id'),
        title=title,
        provider=data.get('provider', '').strip(),
        description=data.get('description', '').strip(),
        exam_link=data.get('exam_link', '').strip(),
        cover_image=data.get('cover_image') or None,
        difficulty=data.get('difficulty', 'Intermediate'),
        status=data.get('status', 'published'),
        position_x=data.get('position_x') if data.get('position_x') is not None else 0,
        position_y=data.get('position_y') if data.get('position_y') is not None else 0,
        author_id=g.current_user.id
    )
    db.session.add(certification)
    db.session.commit()

    log_audit('CERTIFICATION_CREATE', target_type='Certification', target_id=certification.id, details={'title': title})
    return jsonify(certification.to_dict()), 201

@certification_bp.route('/<int:certification_id>', methods=['PUT', 'DELETE'])
@require_role('teacher', 'admin', 'root_admin')
def modify_certification(certification_id):
    certification = Certification.query.get_or_404(certification_id)

    if request.method == 'DELETE':
        db.session.delete(certification)
        db.session.commit()
        log_audit('CERTIFICATION_DELETE', target_type='Certification', target_id=certification_id)
        return jsonify({'message': 'Certification deleted successfully'}), 200

    data = request.get_json() or {}
    if 'title' in data:
        certification.title = data['title'].strip()
    if 'provider' in data:
        certification.provider = data['provider'].strip()
    if 'description' in data:
        certification.description = data['description'].strip()
    if 'exam_link' in data:
        certification.exam_link = data['exam_link'].strip()
    if 'cover_image' in data:
        certification.cover_image = data['cover_image']
    if 'difficulty' in data:
        certification.difficulty = data['difficulty']
    if 'status' in data:
        certification.status = data['status']
    if 'category_id' in data:
        certification.category_id = data['category_id']

    db.session.commit()
    log_audit('CERTIFICATION_UPDATE', target_type='Certification', target_id=certification_id)
    return jsonify(certification.to_dict()), 200


# --- Categories (the "flowchart" grouping) ---

@certification_category_bp.route('', methods=['GET'])
@require_auth
def list_categories():
    categories = CertificationCategory.query.order_by(CertificationCategory.created_at).all()
    return jsonify([c.to_dict() for c in categories]), 200

@certification_category_bp.route('', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def create_category():
    data = request.get_json() or {}
    slug = (data.get('slug') or '').strip()
    title = (data.get('title') or '').strip()

    if not slug or not title:
        return jsonify({'error': 'Slug and title are required'}), 400

    if CertificationCategory.query.filter_by(slug=slug).first():
        return jsonify({'error': 'A category with this slug already exists'}), 409

    category = CertificationCategory(
        slug=slug,
        title=title,
        description=(data.get('description') or '').strip(),
        created_by=g.current_user.id
    )
    db.session.add(category)
    db.session.commit()

    log_audit('CERTIFICATION_CATEGORY_CREATED', target_type='CertificationCategory', target_id=category.id,
              notes=f"Category '{slug}' created by {g.current_user.username}")
    return jsonify(category.to_dict()), 201

@certification_category_bp.route('/<slug>', methods=['PUT'])
@require_role('teacher', 'admin', 'root_admin')
def update_category(slug):
    category = CertificationCategory.query.filter_by(slug=slug).first_or_404()
    data = request.get_json() or {}

    if 'title' in data and data['title']:
        category.title = data['title'].strip()
    if 'description' in data:
        category.description = (data['description'] or '').strip()

    db.session.commit()
    log_audit('CERTIFICATION_CATEGORY_UPDATED', target_type='CertificationCategory', target_id=category.id,
              notes=f"Category '{slug}' updated by {g.current_user.username}")
    return jsonify(category.to_dict()), 200

@certification_category_bp.route('/<slug>', methods=['DELETE'])
@require_role('teacher', 'admin', 'root_admin')
def delete_category(slug):
    # Certifications in this category are NOT deleted - category_id is
    # ON DELETE SET NULL, so they just become uncategorized rather than
    # vanishing along with the grouping they happened to be filed under.
    category = CertificationCategory.query.filter_by(slug=slug).first_or_404()
    db.session.delete(category)
    db.session.commit()
    log_audit('CERTIFICATION_CATEGORY_DELETED', target_type='CertificationCategory', target_id=category.id,
              notes=f"Category '{slug}' deleted by {g.current_user.username}")
    return jsonify({'message': f"Category '{slug}' deleted successfully"}), 200

@certification_category_bp.route('/<slug>/full', methods=['GET'])
@require_auth
def get_category_full(slug):
    category = CertificationCategory.query.filter_by(slug=slug).first_or_404()

    if g.current_user.role in ['teacher', 'admin', 'root_admin']:
        certifications = Certification.query.filter_by(category_id=category.id).order_by(Certification.id).all()
    else:
        certifications = Certification.query.filter_by(category_id=category.id, status='published').order_by(Certification.id).all()

    edges = CertificationEdge.query.filter_by(category_id=category.id).order_by(CertificationEdge.order_index).all()

    return jsonify({
        'category': category.to_dict(),
        'certifications': [c.to_dict() for c in certifications],
        'edges': [e.to_dict() for e in edges]
    }), 200

@certification_category_bp.route('/<slug>/layout', methods=['PUT'])
@require_role('teacher', 'admin', 'root_admin')
def save_category_layout(slug):
    """Bulk save: certification card positions + this category's full edge
    set, in one transaction - mirrors save_roadmap_layout. This is what the
    Certification Studio's "Save Layout" button hits after an admin has
    dragged cards / drawn connections."""
    category = CertificationCategory.query.filter_by(slug=slug).first_or_404()
    data = request.get_json() or {}
    cert_updates = data.get('certifications', [])
    new_edges = data.get('edges', [])

    valid_cert_ids = {c.id for c in Certification.query.filter_by(category_id=category.id).all()}

    for cu in cert_updates:
        cert_id = cu.get('id')
        if cert_id not in valid_cert_ids:
            continue
        cert = Certification.query.get(cert_id)
        if 'position_x' in cu:
            cert.position_x = cu['position_x']
        if 'position_y' in cu:
            cert.position_y = cu['position_y']

    CertificationEdge.query.filter_by(category_id=category.id).delete()
    seen_pairs = set()
    for idx, e in enumerate(new_edges):
        source_id = e.get('source_cert_id')
        target_id = e.get('target_cert_id')
        if source_id not in valid_cert_ids or target_id not in valid_cert_ids:
            continue
        pair = (source_id, target_id)
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        db.session.add(CertificationEdge(
            category_id=category.id,
            source_cert_id=source_id,
            target_cert_id=target_id,
            label=e.get('label'),
            order_index=idx + 1
        ))

    db.session.commit()
    log_audit('CERTIFICATION_LAYOUT_SAVED', target_type='CertificationCategory', target_id=category.id,
              notes=f"Layout saved for '{slug}' by {g.current_user.username}",
              details={'cert_count': len(cert_updates), 'edge_count': len(seen_pairs)})

    return jsonify({'message': 'Layout saved successfully'}), 200
