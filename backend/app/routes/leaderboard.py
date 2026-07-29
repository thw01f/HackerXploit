from flask import Blueprint, jsonify
from app.models import db, User, CompetitionParticipation, Enrollment
from app.utils.decorators import require_auth
from app.services.ctfd_sync import fetch_ctfd_scores

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/api/leaderboard', methods=['GET'])
@require_auth
def get_leaderboard():
    users = User.query.filter(User.status == 'approved').all()
    ctfd_data = fetch_ctfd_scores()

    rankings = []
    for u in users:
        wins_count = CompetitionParticipation.query.filter_by(user_id=u.id, result='winner').count()
        runners_count = CompetitionParticipation.query.filter_by(user_id=u.id, result='runner_up').count()
        participations_count = CompetitionParticipation.query.filter_by(user_id=u.id).count()
        courses_count = Enrollment.query.filter_by(user_id=u.id, progress_percent=100.0).count()

        ctf_stats = ctfd_data.get(u.email.lower()) or ctfd_data.get(u.username.lower()) or {'score': 0, 'solves': 0}
        ctf_score = float(ctf_stats.get('score', 0))
        ctf_solves = ctf_stats.get('solves', 0)

        # Leaderboard ranking score strictly based on CTFd score
        u.leaderboard_score = round(ctf_score, 1)

        rankings.append({
            'user_id': u.id,
            'username': u.username,
            'full_name': u.full_name or u.username,
            'avatar_url': u.avatar_url,
            'role': u.role,
            'academic_year': u.academic_year,
            'specialization_role': u.specialization_role,
            'leaderboard_score': u.leaderboard_score,
            'ctfd_score': ctf_score,
            'ctfd_solves': ctf_solves,
            'events_attended': participations_count,
            'competition_wins': wins_count,
            'competition_runner_ups': runners_count,
            'courses_completed': courses_count
        })

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

    # Sort rankings strictly by CTFd score descending
    rankings.sort(key=lambda x: (x['ctfd_score'], x['ctfd_solves']), reverse=True)
    for idx, item in enumerate(rankings, start=1):
        item['rank'] = idx

    return jsonify({'leaderboard': rankings}), 200
