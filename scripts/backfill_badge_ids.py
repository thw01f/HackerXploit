"""
One-time backfill: permanently assigns a sequential Badge ID to every
approved user who doesn't already have one persisted, in account-creation
order. Safe to re-run - users who already have a badge_id are skipped.

Usage:
    docker compose exec web python /app/../scripts/backfill_badge_ids.py
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

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
