from flask import Blueprint, jsonify
from app.models import db, User, CompetitionParticipation, Enrollment
from app.utils.decorators import require_auth

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/api/leaderboard', methods=['GET'])
@require_auth
def get_leaderboard():
    users = User.query.filter(
        User.status == 'approved'
    ).order_by(User.leaderboard_score.desc(), User.username.asc()).limit(100).all()

    rankings = []
    for rank, u in enumerate(users, start=1):
        # Calculate stats breakdown
        wins_count = CompetitionParticipation.query.filter_by(user_id=u.id, result='winner').count()
        runners_count = CompetitionParticipation.query.filter_by(user_id=u.id, result='runner_up').count()
        courses_count = Enrollment.query.filter_by(user_id=u.id, progress_percent=100.0).count()

        rankings.append({
            'rank': rank,
            'user_id': u.id,
            'username': u.username,
            'full_name': u.full_name or u.username,
            'avatar_url': u.avatar_url,
            'role': u.role,
            'leaderboard_score': round(u.leaderboard_score or 0.0, 1),
            'competition_wins': wins_count,
            'competition_runner_ups': runners_count,
            'courses_completed': courses_count
        })

    return jsonify({'leaderboard': rankings}), 200
