"""
One-time backfill: permanently assigns a sequential Badge ID to every
approved user who doesn't already have one persisted, in account-creation
order. Safe to re-run - users who already have a badge_id are skipped.

Usage:
    docker compose exec web python /app/../scripts/backfill_badge_ids.py
"""
import sys
import os

# See scripts/init_db.py for why both candidates are needed - host/dev layout
# vs. the web container's layout (scripts/ bind-mounted alongside /app, which
# IS the backend root there, not /app/backend).
_here = os.path.dirname(os.path.abspath(__file__))
for _candidate in (os.path.join(_here, '../backend'), os.path.dirname(_here)):
    _candidate = os.path.abspath(_candidate)
    if _candidate not in sys.path:
        sys.path.insert(0, _candidate)

from app import create_app
from app.models import db, User


def backfill():
    app = create_app()
    with app.app_context():
        users = User.query.filter(
            User.status == 'approved',
            User.badge_id.is_(None)
        ).order_by(User.created_at.asc()).all()

        if not users:
            print("Nothing to backfill - every approved user already has a Badge ID.")
            return

        for user in users:
            badge_id = user.assign_badge_id()
            print(f"Assigned {badge_id} to @{user.username} (role={user.role})")

        db.session.commit()
        print(f"Backfilled {len(users)} Badge ID(s).")


if __name__ == '__main__':
    backfill()
