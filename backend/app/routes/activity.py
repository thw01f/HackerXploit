import time
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g, current_app
from app.models import db, User, ActivityHeartbeat, ActivitySession
from app.utils.decorators import require_auth
from redis import Redis

activity_bp = Blueprint('activity', __name__)

def get_redis():
    redis_url = current_app.config.get('REDIS_URL', 'redis://redis:6379/0')
    try:
        return Redis.from_url(redis_url)
    except Exception:
        return None

@activity_bp.route('/api/heartbeat', methods=['POST'])
@require_auth
def send_heartbeat():
    data = request.get_json(silent=True) or {}
    subdomain = data.get('subdomain', 'club')

    user = g.current_user
    now = datetime.utcnow()
    user.last_seen_at = now

    # Record raw heartbeat ping
    hb = ActivityHeartbeat(
        user_id=user.id,
        subdomain=subdomain,
        ts=now
    )
    db.session.add(hb)
    db.session.commit()

    # Set Redis key online:<user_id> with 90s TTL (zero-DB scan for "who's online")
    r = get_redis()
    if r:
        try:
            r.setex(f"online:{user.id}", 90, f"{subdomain}:{int(time.time())}")
        except Exception as e:
            current_app.logger.warning(f"Redis heartbeat error: {e}")

    return jsonify({
        'status': 'ok',
        'last_seen_at': user.last_seen_at.isoformat()
    }), 200

@activity_bp.route('/api/activity/online', methods=['GET'])
@require_auth
def get_online_users():
    """Returns currently online user IDs by scanning online:* keys in Redis (O(1) / zero DB hit)"""
    r = get_redis()
    online_user_ids = []

    if r:
        try:
            keys = r.keys("online:*")
            for k in keys:
                key_str = k.decode('utf-8') if isinstance(k, bytes) else str(k)
                parts = key_str.split(':')
                if len(parts) == 2 and parts[1].isdigit():
                    online_user_ids.append(int(parts[1]))
        except Exception as e:
            current_app.logger.warning(f"Redis scan error: {e}")

    # Fallback to users seen in last 2 minutes if Redis isn't reachable
    if not online_user_ids and not r:
        two_mins_ago = datetime.utcnow() - timedelta(minutes=2)
        users = User.query.filter(User.last_seen_at >= two_mins_ago).all()
        online_user_ids = [u.id for u in users]

    return jsonify({
        'online_count': len(online_user_ids),
        'online_user_ids': online_user_ids
    }), 200

@activity_bp.route('/api/activity/stats/<int:user_id>', methods=['GET'])
@require_auth
def get_user_activity_stats(user_id):
    user = User.query.get_or_404(user_id)

    # 30-day activity sessions
    thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
    sessions = ActivitySession.query.filter(
        ActivitySession.user_id == user.id,
        ActivitySession.date >= thirty_days_ago
    ).all()

    total_seconds = sum(s.duration_seconds for s in sessions)

    subdomain_seconds = {'club': 0, 'ctf': 0, 'intro': 0}
    daily_map = {}
    for i in range(30):
        d_str = (datetime.utcnow() - timedelta(days=29 - i)).strftime('%Y-%m-%d')
        daily_map[d_str] = 0.0

    for s in sessions:
        subdomain_seconds[s.subdomain] = subdomain_seconds.get(s.subdomain, 0) + s.duration_seconds
        if s.date in daily_map:
            daily_map[s.date] += round(s.duration_seconds / 3600.0, 2)

    chart_data = [{'date': d, 'hours': daily_map[d]} for d in sorted(daily_map.keys())]

    return jsonify({
        'user_id': user.id,
        'total_hours': round(total_seconds / 3600.0, 1),
        'subdomain_breakdown_hours': {
            k: round(v / 3600.0, 1) for k, v in subdomain_seconds.items()
        },
        'chart_data': chart_data
    }), 200
