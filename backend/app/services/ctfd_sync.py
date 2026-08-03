import os
import subprocess
import json

# CTFd's database lives on the persisted ctfd_db_data named volume, not the
# container's ephemeral writable layer (see docker-compose.yml's
# DATABASE_URL=sqlite:////var/ctfd_data/ctfd.db for the ctfd service, and
# scripts/init_ctfd.py which already used this correct path). This module
# previously hardcoded /tmp/ctfd.db - a path CTFd itself never reads, and
# because sqlite3.connect() auto-creates a file at whatever path it's given,
# every call here was silently succeeding against a schema-less throwaway
# file instead of erroring, meaning CTFd sync has been a complete no-op
# (provisioning, suspend/reinstate, role changes, deletion - all of it)
# since CTFd's database was moved onto a named volume.
CTFD_DB_PATH = os.getenv('CTFD_DB_PATH', '/var/ctfd_data/ctfd.db')


def _run_ctfd_script(py_script, payload=None, label='CTFd Sync'):
    """
    Shared subprocess runner for every function below - execs into the
    running CTFd container and runs `py_script` against its real database.
    Unlike the previous per-function implementations, this actually checks
    the subprocess exit code and stderr instead of unconditionally returning
    True, so a real failure (container down, script exception, DB locked)
    is visible and correctly reported instead of silently claiming success.
    """
    cmd = ['docker', 'exec', '-i', 'hx_ctfd', 'python', '-c', py_script]
    try:
        res = subprocess.run(
            cmd,
            input=json.dumps(payload) if payload is not None else None,
            capture_output=True, text=True, timeout=5
        )
    except Exception as e:
        print(f"[{label} Error] Failed to reach CTFd container: {e}")
        return False, ''

    if res.stdout.strip():
        print(f"[{label} Output]: {res.stdout.strip()}")
    if res.returncode != 0:
        print(f"[{label} Error] Exit code {res.returncode}: {res.stderr.strip()}")
        return False, res.stdout.strip()
    return True, res.stdout.strip()


def sync_user_to_ctfd(user, old_username=None, old_email=None):
    """
    Directly provisions or updates an approved user inside the running CTFd Docker container ('hx_ctfd')
    so they appear in CTFd instantly upon admin approval or profile/onboarding updates.
    Syncs Full Name, Roll No/Student ID, Academic Year, Department, Bio, Specialization, and Portfolios.

    old_username/old_email: pass the pre-update values when a caller is about
    to rename/re-email a user (e.g. update_user_details) so the lookup below
    can still find the existing CTFd row even after both fields changed at
    once - matching on the new values alone would find nothing and silently
    create a second, orphaned CTFd account instead of updating the real one.
    """
    try:
        # Build detailed affiliation string for CTFd
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

        # Build website string with Bio & social links
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

        payload = {
            'username': user.username,
            'name': full_name,
            'email': user.email,
            'old_username': old_username or user.username,
            'old_email': old_email or user.email,
            'is_admin': getattr(user, 'is_root_admin', False) or user.role == 'admin',
            'affiliation': affiliation_str,
            'website': website_str,
            # A suspended platform account must not be able to keep using an
            # already-open CTFd session - ban mirrors the platform's status
            # so suspend/reinstate on this side take effect in CTFd too.
            'banned': getattr(user, 'status', '') == 'suspended',
            'db_path': CTFD_DB_PATH
        }

        py_script = """
import sys, json, sqlite3, secrets
data = json.loads(sys.stdin.read())
conn = sqlite3.connect(data['db_path'])
cur = conn.cursor()

# Match on old OR new username/email - a caller may have just renamed and/or
# re-emailed this user in the same request (update_user_details), so the
# pre-update values are the only way to still find the existing CTFd row.
cur.execute(
    "SELECT id FROM users WHERE name IN (?, ?) OR email IN (?, ?);",
    (data['username'], data['old_username'], data['email'], data['old_email'])
)
row = cur.fetchone()

role_type = 'admin' if data['is_admin'] else 'user'
banned_flag = 1 if data.get('banned') else 0

if not row:
    # Each provisioned account gets its own random, never-disclosed password so CTFd's
    # native local login cannot be used to impersonate a member (SSO is the only login path).
    from passlib.hash import bcrypt_sha256
    random_password_hash = bcrypt_sha256.hash(secrets.token_urlsafe(32))
    cur.execute('''
        INSERT INTO users (name, email, password, type, verified, hidden, banned, affiliation, website, created)
        VALUES (?, ?, ?, ?, 1, 0, ?, ?, ?, CURRENT_TIMESTAMP);
    ''', (data['username'], data['email'], random_password_hash, role_type, banned_flag, data['affiliation'], data['website']))
    conn.commit()
    print("[CTFd Sync] Created user:", data['username'])
else:
    cur.execute('''
        UPDATE users SET name = ?, email = ?, affiliation = ?, website = ?, type = ?, banned = ? WHERE id = ?;
    ''', (data['username'], data['email'], data['affiliation'], data['website'], role_type, banned_flag, row[0]))
    conn.commit()
    print("[CTFd Sync] Updated user:", data['username'])

conn.close()
"""
        ok, _ = _run_ctfd_script(py_script, payload, label='CTFd Sync')
        return ok
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
    and solve counts for all registered users directly from CTFd DB.
    Returns a dict mapping lowercase email and username -> { 'score': int, 'solves': int }
    """
    try:
        py_script = f"""
import sqlite3, json
conn = sqlite3.connect({CTFD_DB_PATH!r})
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
conn.close()
res = {{}}
for r in rows:
    data = {{'score': r[2], 'solves': r[3]}}
    if r[0]:
        res[r[0]] = data
    if r[1]:
        res[r[1]] = data
print(json.dumps(res))
"""
        cmd = ['docker', 'exec', 'hx_ctfd', 'python', '-c', py_script]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if res.returncode == 0 and res.stdout.strip():
            return json.loads(res.stdout.strip())
        elif res.returncode != 0:
            print(f"[CTFd Scores Fetch Error] Exit code {res.returncode}: {res.stderr.strip()}")
    except Exception as e:
        print(f"[CTFd Scores Fetch Error]: {e}")
    return {}

def delete_user_from_ctfd(username, email):
    """
    Permanently delete a user from CTFd SQLite database when deleted by an admin in HackerXploit.
    """
    try:
        payload = {
            'username': username,
            'email': email,
            'db_path': CTFD_DB_PATH
        }
        py_script = """
import sys, json, sqlite3
data = json.loads(sys.stdin.read())
conn = sqlite3.connect(data['db_path'])
cur = conn.cursor()

cur.execute("SELECT id FROM users WHERE name = ? OR email = ?;", (data['username'], data['email']))
row = cur.fetchone()

if row:
    user_id = row[0]
    # Every core CTFd table that can hold a user_id FK - deleted individually
    # (not one big try/except) so one missing/renamed table on a given CTFd
    # version can't block cleanup of the rest, and so the final DELETE FROM
    # users below isn't silently skipped by a FK violation from a table we
    # forgot, the way the previous version of this script could be.
    for table in ('solves', 'submissions', 'tracking', 'awards', 'unlocks', 'notifications'):
        try:
            cur.execute(f"DELETE FROM {table} WHERE user_id = ?;", (user_id,))
        except sqlite3.OperationalError as e:
            print(f"[CTFd Delete] Skipped {table}:", e)
    conn.commit()

    try:
        cur.execute("DELETE FROM users WHERE id = ?;", (user_id,))
        conn.commit()
        print("[CTFd Delete] Deleted user:", data['username'])
    except sqlite3.IntegrityError as e:
        print("[CTFd Delete] FAILED - user row still referenced elsewhere:", e)
else:
    print("[CTFd Delete] No matching CTFd user for:", data['username'])

conn.close()
"""
        ok, _ = _run_ctfd_script(py_script, payload, label='CTFd Delete')
        return ok
    except Exception as e:
        print(f"[CTFd Delete Error]: {e}")
        return False
