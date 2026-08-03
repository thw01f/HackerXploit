"""
Writes the platform's OAuth2 client credentials into CTFd's OWN database so
CTFd can act as the OAuth consumer for "Login with HackerXploit" SSO.

This used to connect directly to the platform's Postgres database and write
into a table literally named `config` - which doesn't exist there at all
(Postgres has no such table; CTFd's `config` table lives in CTFd's own,
completely separate SQLite database at /var/ctfd_data/ctfd.db). That meant
every run silently hit the "table does not exist" early-return branch and
did nothing - CTFd's oauth_client_id/oauth_authorization_endpoint/etc. were
never actually set, so CTFd never showed an SSO login option and the only
way in was CTFd's own native login form, which can never work (CTFd shadow
accounts get a random, never-exposed password - see ctfd_sync.py).

Fixed to write into CTFd's real database, the same way every other
CTFd-touching script in this repo does it (see hx-backup.sh,
install-ctfd-theme.sh): `docker exec` into the CTFd container and talk to
its SQLite file directly, since the host has no other access to it.
"""
import sys
import os
import json
import subprocess
from urllib.parse import urlparse


def init_ctfd_oauth():
    # See scripts/init_db.py for why both candidates are needed - host/dev
    # layout vs. the web container's layout (scripts/ bind-mounted alongside
    # /app, which IS the backend root there, not /app/backend).
    _here = os.path.dirname(os.path.abspath(__file__))
    for _candidate in (os.path.join(_here, '../backend'), os.path.dirname(_here)):
        _candidate = os.path.abspath(_candidate)
        if _candidate not in sys.path:
            sys.path.insert(0, _candidate)
    from app import create_app
    from app.models import OAuth2Client

    client_id_lookup = os.getenv('CTFD_OAUTH_CLIENT_ID', 'ctfd-client-id-hx99')

    app = create_app()
    with app.app_context():
        client = OAuth2Client.query.filter_by(client_id=client_id_lookup).first()
        if not client:
            print(f"No OAuth2Client with client_id={client_id_lookup!r} found on the platform - run init_db.py first.")
            return
        client_id = client.client_id
        client_secret = client.client_secret

    # oauth_authorization_endpoint is a browser redirect (user-facing), so it
    # needs the public domain. oauth_token_endpoint/oauth_api_endpoint are
    # server-to-server calls CTFd makes internally, so they use the docker
    # network hostname - matches how REDIS_URL/DATABASE_URL etc. already
    # address the web service elsewhere in docker-compose.yml.
    public_auth_base = os.getenv('CTFD_OAUTH_PUBLIC_BASE_URL', 'https://club.hackerxploit.org')
    internal_web_base = os.getenv('CTFD_OAUTH_INTERNAL_WEB_URL', 'http://web:5000')

    oauth_configs = {
        'oauth_client_id': client_id,
        'oauth_client_secret': client_secret,
        'oauth_authorization_endpoint': f'{public_auth_base}/oauth/authorize',
        'oauth_token_endpoint': f'{internal_web_base}/oauth/token',
        'oauth_api_endpoint': f'{internal_web_base}/oauth/userinfo'
    }

    container = os.getenv('CTFD_CONTAINER', 'hx_ctfd')
    db_path = os.getenv('CTFD_DB_PATH', '/var/ctfd_data/ctfd.db')

    # CTFd's config table has no unique constraint on `key` (just an
    # autoincrement `id` primary key), so ON CONFLICT can't target it -
    # check-then-update-or-insert instead, same as install-ctfd-theme.sh.
    script = f"""
import sqlite3
conn = sqlite3.connect({db_path!r})
cur = conn.cursor()
configs = {json.dumps(oauth_configs)}
for key, value in configs.items():
    cur.execute("SELECT id FROM config WHERE key = ?", (key,))
    if cur.fetchone():
        cur.execute("UPDATE config SET value = ? WHERE key = ?", (value, key))
    else:
        cur.execute("INSERT INTO config (key, value) VALUES (?, ?)", (key, value))
conn.commit()
conn.close()
print("ok")
"""

    try:
        result = subprocess.run(
            ['docker', 'exec', '-i', container, 'python', '-c', script],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and 'ok' in result.stdout:
            print("Successfully initialized CTFd OAuth2 configuration in CTFd's own database!")

            # CTFd memoizes every config value it reads and only busts that
            # cache when its own Python set_config() writes it - not when the
            # row is changed directly in SQLite like above. Without this, the
            # new oauth_* values can sit invisible, served stale from cache,
            # until CTFd's cache entry happens to expire on its own.
            redis_container = os.getenv('REDIS_CONTAINER', 'hx_redis')
            redis_cache_db = os.getenv('REDIS_CACHE_DB', '1')
            # Once Redis has a requirepass set (docker-compose.yml's
            # REDIS_PASSWORD), redis-cli needs -a or it prints "NOAUTH
            # Authentication required" and - critically - still exits 0, so
            # checking returncode alone (the previous version of this code)
            # silently reported success on a flush that never happened.
            # There's no separate REDIS_PASSWORD env var passed to whatever
            # runs this script, only REDIS_URL - parse it out of that.
            redis_password = None
            redis_url = os.getenv('REDIS_URL', '')
            parsed = urlparse(redis_url)
            if parsed.password:
                redis_password = parsed.password
            redis_cmd = ['docker', 'exec', redis_container, 'redis-cli']
            if redis_password:
                redis_cmd += ['-a', redis_password]
            redis_cmd += ['-n', redis_cache_db, 'FLUSHDB']
            flush = subprocess.run(redis_cmd, capture_output=True, text=True, timeout=10)
            if 'OK' in flush.stdout:
                print("CTFd config cache flushed (change is live immediately).")
            else:
                print(f"Note: could not flush CTFd's config cache ({(flush.stderr or flush.stdout).strip()}) - the change may take a moment to appear.")
        else:
            print(f"CTFd OAuth initialization note: {result.stderr or result.stdout}")
    except Exception as e:
        # Not fatal - e.g. running inside a container without docker socket
        # access during an automated deploy. Run this script from the host
        # (like install-ctfd-theme.sh) if this happens.
        print(f"CTFd OAuth initialization note: {e}")


if __name__ == '__main__':
    init_ctfd_oauth()
