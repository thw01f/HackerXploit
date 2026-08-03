import os
import sqlite3
import secrets

# CTFd's database lives on the persisted ctfd_db_data named volume (see
# docker-compose.yml's DATABASE_URL=sqlite:////var/ctfd_data/ctfd.db for the
# ctfd service). This module used to shell out to `docker exec` into the
# ctfd container and run a Python script against the file from there - that
# only works when whatever calls it has Docker socket/CLI access, which the
# web container deliberately does not have (mounting the socket there would
# give a compromised Flask app root-equivalent control of the whole host).
# Instead, docker-compose.yml now mounts the same ctfd_db_data volume
# read-write into web too, and every function below talks to the SQLite file
# directly. SQLite handles multiple processes (this one, CTFd's own gunicorn
# workers) safely via file locking - the timeout below just waits out any
# brief lock contention instead of failing immediately.
CTFD_DB_PATH = os.getenv('CTFD_DB_PATH', '/var/ctfd_data/ctfd.db')
_DB_TIMEOUT_SECONDS = 10


def _connect():
    return sqlite3.connect(CTFD_DB_PATH, timeout=_DB_TIMEOUT_SECONDS)


def sync_user_to_ctfd(user, old_username=None, old_email=None):
    """
    Directly provisions or updates an approved user inside CTFd's own database
    so they appear in CTFd instantly upon admin approval or profile/onboarding updates.
    Syncs Full Name, Roll No/Student ID, Academic Year, Department, Bio, Specialization, and Portfolios.

    old_username/old_email: pass the pre-update values when a caller is about
    to rename/re-email a user (e.g. update_user_details) so the lookup below
    can still find the existing CTFd row even after both fields changed at
    once - matching on the new values alone would find nothing and silently
    create a second, orphaned CTFd account instead of updating the real one.
    """
    try:
        role_label = getattr(user, 'specialization_role', None) or ("Teacher" if user.role == "teacher" else "Member")
        full_name = getattr(user, 'full_name', '') or user.username
        student_id = getattr(user, 'student_id', '') or ''
        dept_str = getattr(user, 'department', '') or "Cyber Security"
        yr_str = getattr(user, 'academic_year', '') or ''

        badge_id = getattr(user, 'get_badge_id', lambda: '')() or getattr(user, 'badge_id', '') or f"HX-USER-{getattr(user, 'id', 0):04d}"
        aff_parts = [f"Badge ID: {badge_id}", role_label]
        if full_name:
            aff_parts.append(f"Name: {full_name}")
        if student_id:
            aff_parts.append(f"ID: {student_id}")
        if dept_str:
            aff_parts.append(f"Dept: {dept_str}")
        if yr_str:
            aff_parts.append(f"Year {yr_str}")

        affiliation_str = " | ".join(aff_parts)

        website_url = getattr(user, 'website_url', '') or ""
        bio_str = getattr(user, 'bio', '') or ""

        social_parts = []
        if website_url:
            social_parts.append(website_url)
        if bio_str:
            social_parts.append(f"Bio: {bio_str}")
        if getattr(user, 'github_url', None):
            social_parts.append(f"GH: {user.github_url}")
        if getattr(user, 'linkedin_url', None):
            social_parts.append(f"IN: {user.linkedin_url}")
        if getattr(user, 'tryhackme_url', None):
            social_parts.append(f"THM: {user.tryhackme_url}")
        if getattr(user, 'htb_url', None):
            social_parts.append(f"HTB: {user.htb_url}")

        website_str = " | ".join(social_parts)

        username = user.username
        email = user.email
        old_username = old_username or username
        old_email = old_email or email
        is_admin = getattr(user, 'is_root_admin', False) or user.role == 'admin'
        role_type = 'admin' if is_admin else 'user'
        banned_flag = 1 if getattr(user, 'status', '') == 'suspended' else 0

        conn = _connect()
        try:
            cur = conn.cursor()
            # Match on old OR new username/email - a caller may have just
            # renamed and/or re-emailed this user in the same request
            # (update_user_details), so the pre-update values are the only
            # way to still find the existing CTFd row.
            cur.execute(
                "SELECT id FROM users WHERE name IN (?, ?) OR email IN (?, ?);",
                (username, old_username, email, old_email)
            )
            row = cur.fetchone()

            if not row:
                # Each provisioned account gets its own random, never-disclosed
                # password so CTFd's native local login cannot be used to
                # impersonate a member (SSO is the only login path).
                from passlib.hash import bcrypt_sha256
                random_password_hash = bcrypt_sha256.hash(secrets.token_urlsafe(32))
                cur.execute('''
                    INSERT INTO users (name, email, password, type, verified, hidden, banned, affiliation, website, created)
                    VALUES (?, ?, ?, ?, 1, 0, ?, ?, ?, CURRENT_TIMESTAMP);
                ''', (username, email, random_password_hash, role_type, banned_flag, affiliation_str, website_str))
                conn.commit()
                print("[CTFd Sync] Created user:", username)
            else:
                cur.execute('''
                    UPDATE users SET name = ?, email = ?, affiliation = ?, website = ?, type = ?, banned = ? WHERE id = ?;
                ''', (username, email, affiliation_str, website_str, role_type, banned_flag, row[0]))
                conn.commit()
                print("[CTFd Sync] Updated user:", username)
            return True
        finally:
            conn.close()
    except Exception as e:
        print(f"[CTFd Sync Error]: {e}")
        return False


def sync_all_users_to_ctfd(users_list):
    """
    Bulk sync all approved users to CTFd container
    """
    for u in users_list:
        if getattr(u, 'status', '') == 'approved':
            sync_user_to_ctfd(u)


def fetch_ctfd_scores():
    """
    Retrieves real-time CTFd scores (including challenge solves and administrative awards)
    and solve counts for all registered users directly from CTFd's database.
    Returns a dict mapping lowercase email and username -> { 'score': int, 'solves': int }
    """
    try:
        conn = _connect()
        try:
            cur = conn.cursor()
            query = '''
                SELECT
                    LOWER(u.email),
                    LOWER(u.name),
                    COALESCE(s_sum.solve_score, 0) + COALESCE(a_sum.award_score, 0) AS total_score,
                    COALESCE(s_sum.solve_count, 0) AS solves
                FROM users u
                LEFT JOIN (
                    SELECT s.user_id, COALESCE(SUM(c.value), 0) AS solve_score, COUNT(s.id) AS solve_count
                    FROM solves s
                    JOIN challenges c ON s.challenge_id = c.id
                    GROUP BY s.user_id
                ) s_sum ON u.id = s_sum.user_id
                LEFT JOIN (
                    SELECT a.user_id, COALESCE(SUM(a.value), 0) AS award_score
                    FROM awards a
                    GROUP BY a.user_id
                ) a_sum ON u.id = a_sum.user_id
                WHERE u.banned = 0;
            '''
            rows = cur.execute(query).fetchall()
        finally:
            conn.close()

        res = {}
        for email, name, score, solves in rows:
            data = {'score': score, 'solves': solves}
            if email:
                res[email] = data
            if name:
                res[name] = data
        return res
    except Exception as e:
        print(f"[CTFd Scores Fetch Error]: {e}")
        return {}


def delete_user_from_ctfd(username, email):
    """
    Permanently delete a user from CTFd's database when deleted by an admin in HackerXploit.
    """
    try:
        conn = _connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE name = ? OR email = ?;", (username, email))
            row = cur.fetchone()

            if not row:
                print("[CTFd Delete] No matching CTFd user for:", username)
                return True

            user_id = row[0]
            # Every core CTFd table that can hold a user_id FK - deleted
            # individually (not one big try/except) so one missing/renamed
            # table on a given CTFd version can't block cleanup of the rest,
            # and so the final DELETE FROM users below isn't silently skipped
            # by a FK violation from a table we forgot.
            for table in ('solves', 'submissions', 'tracking', 'awards', 'unlocks', 'notifications'):
                try:
                    cur.execute(f"DELETE FROM {table} WHERE user_id = ?;", (user_id,))
                except sqlite3.OperationalError as e:
                    print(f"[CTFd Delete] Skipped {table}:", e)
            conn.commit()

            try:
                cur.execute("DELETE FROM users WHERE id = ?;", (user_id,))
                conn.commit()
                print("[CTFd Delete] Deleted user:", username)
                return True
            except sqlite3.IntegrityError as e:
                print("[CTFd Delete] FAILED - user row still referenced elsewhere:", e)
                return False
        finally:
            conn.close()
    except Exception as e:
        print(f"[CTFd Delete Error]: {e}")
        return False
