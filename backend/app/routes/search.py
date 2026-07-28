from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from app.models import db, Course
from app.utils.decorators import require_auth

search_bp = Blueprint('search', __name__, url_prefix='/api/search')

@search_bp.route('', methods=['GET'])
@require_auth
def site_search():
    query_str = request.args.get('q', '').strip()
    if not query_str:
        return jsonify({'results': []}), 200

    results = []

    # 1. Search Courses
    try:
        # PostgreSQL Full-Text Search tsvector attempt
        sql_query = """
            SELECT id, title, slug, description, cover_image, 'course' as type
            FROM courses
            WHERE to_tsvector('english', title || ' ' || description) @@ plainto_tsquery('english', :q)
               OR title ILIKE :like_q OR description ILIKE :like_q;
        """
        rows = db.session.execute(db.text(sql_query), {'q': query_str, 'like_q': f"%{query_str}%"}).fetchall()
        for r in rows:
            results.append({
                'id': r.id,
                'title': r.title,
                'slug': r.slug,
                'description': r.description[:150] + "..." if len(r.description) > 150 else r.description,
                'type': 'course',
                'link': f"/academy/course/{r.slug}",
                'image': r.cover_image
            })
    except Exception:
        # Fallback query if SQLite in test env
        courses = Course.query.filter(
            or_(Course.title.ilike(f"%{query_str}%"), Course.description.ilike(f"%{query_str}%"))
        ).all()
        for c in courses:
            results.append({
                'id': c.id,
                'title': c.title,
                'slug': c.slug,
                'description': c.description[:150] + "..." if len(c.description) > 150 else c.description,
                'type': 'course',
                'link': f"/academy/course/{c.slug}",
                'image': c.cover_image
            })

    return jsonify({'results': results, 'query': query_str, 'total': len(results)}), 200
