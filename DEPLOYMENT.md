# Deployment Guide: Single DigitalOcean Droplet & Multi-Subdomain Infrastructure

This guide covers deploying the HackerXploit Club Platform on a single DigitalOcean
Droplet using Docker Compose, an automated Let's Encrypt wildcard certificate via
Cloudflare DNS, CTFd SSO, and Cloudflare as the edge proxy. It also covers **updating
an existing deployment** and **troubleshooting** the specific issues this stack has
actually hit in practice - not hypothetical ones. Everything below assumes no prior
Claude/AI session is available: every command is copy-pasteable as-is over SSH.

## Prerequisites

- DigitalOcean Droplet: 4GB RAM / 2 vCPUs minimum recommended (Ubuntu 24.04 LTS).
- Domain registered and its DNS managed by **Cloudflare**: `hackerxploit.org`.
- Two DNS A records in Cloudflare, proxy status **DNS only** (grey cloud) - not
  "Proxied" - while you set things up (you can switch to Proxied afterward; see
  "Cloudflare Proxy Mode" below):
  - `club` -> Droplet IP
  - `arena` -> Droplet IP
  - **Not** the bare `hackerxploit.org` root - it's reserved for other, unrelated
    projects and isn't configured anywhere in this repo's Nginx/Docker Compose setup.
    Point its A record wherever that other project lives, or leave it unset.
- A Cloudflare API Token (not the Global API Key) scoped to **Zone → DNS → Edit** on
  just this one zone. Dashboard → profile icon → **My Profile** → **API Tokens** →
  **Create Custom Token**. Used only to prove DNS control for the wildcard cert.
- A Cloudflare Turnstile widget (Dashboard → **Turnstile** → **Add widget**), hostname
  `club.hackerxploit.org`, mode **Managed**. Gives you a Site Key and Secret Key.

---

## Step 1: Install Docker, Certbot, and Node.js

```bash
# Docker (official repo, not the distro's docker.io/docker-compose packages)
apt update -y
apt install -y ca-certificates curl gnupg git
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update -y
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker

# Certbot + the Cloudflare DNS plugin (fully automates the wildcard cert - no
# manual TXT record copy-pasting, and it self-renews forever via a systemd timer)
apt install -y certbot python3-certbot-dns-cloudflare

# Node.js (needed once, to build the frontend - see Step 4a)
curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
apt install -y nodejs
```

---

## Step 2: Clone & Configure Environment

```bash
mkdir -p /opt/hackerxploit
cd /opt/hackerxploit
git clone https://github.com/thw01f/HackerXploit.git .
```

Generate `.env` with strong secrets (do this on the server so secrets never leave
it). Paste this whole block as one command - it writes `.env` directly:

```bash
python3 - <<'PY'
import secrets
secret_key = secrets.token_hex(32)
pg_pass = secrets.token_hex(24)
redis_pass = secrets.token_hex(24)
ctfd_secret = secrets.token_hex(32)
env = f"""DOMAIN=hackerxploit.org
SECRET_KEY={secret_key}
FLASK_ENV=production
SESSION_COOKIE_DOMAIN=.club.hackerxploit.org
SESSION_COOKIE_SECURE=true

POSTGRES_DB=hackerxploit
POSTGRES_USER=hx_user
POSTGRES_PASSWORD={pg_pass}
DATABASE_URL=postgresql://hx_user:{pg_pass}@db:5432/hackerxploit

REDIS_PASSWORD={redis_pass}
REDIS_URL=redis://:{redis_pass}@redis:6379/0

CTFD_OAUTH_CLIENT_ID=ctfd-client-id-hx99
CTFD_OAUTH_CLIENT_SECRET={ctfd_secret}
CTFD_OAUTH_PUBLIC_BASE_URL=https://club.hackerxploit.org
CTFD_OAUTH_INTERNAL_WEB_URL=http://web:5000

SENTRY_DSN=
VITE_SENTRY_DSN=

# REPLACE these two with your real Turnstile widget keys (see Prerequisites) -
# the stack refuses to boot in production with the placeholder secret key below.
TURNSTILE_SECRET_KEY=1x0000000000000000000000000000000AA
TURNSTILE_SITE_KEY=1x00000000000000000000AA

CLAMAV_HOST=clamav
CLAMAV_PORT=3310
UPLOAD_FOLDER=/var/uploads
REGISTRY_URL=registry.digitalocean.com/hackerxploit
"""
with open('.env', 'w') as f:
    f.write(env)
print("Wrote .env")
PY
chmod 600 .env
```

Then edit in your real Turnstile keys:

```bash
nano .env   # replace TURNSTILE_SECRET_KEY and TURNSTILE_SITE_KEY
```

Optional (real email instead of log-only mode): add `SMTP_HOST`, `SMTP_PORT`,
`SMTP_USER`, `SMTP_PASSWORD`, `SMTP_SENDER` to `.env`. Without these, password
resets/notifications are printed to the `web` container's logs instead of sent.

---

## Step 3: Wildcard SSL Certificate (Certbot + Cloudflare DNS plugin)

```bash
mkdir -p /root/.secrets
cat > /root/.secrets/cloudflare.ini <<'INI'
dns_cloudflare_api_token = YOUR_CLOUDFLARE_API_TOKEN_HERE
INI
chmod 600 /root/.secrets/cloudflare.ini

certbot certonly \
  --dns-cloudflare \
  --dns-cloudflare-credentials /root/.secrets/cloudflare.ini \
  --dns-cloudflare-propagation-seconds 30 \
  -d hackerxploit.org -d "*.hackerxploit.org" \
  --agree-tos --non-interactive -m YOUR_EMAIL_HERE \
  --no-eff-email
```

This proves DNS control automatically via the API token - no manual TXT record
step, and no interaction needed. It also installs a systemd timer
(`systemctl list-timers | grep certbot`) that renews the cert automatically forever;
nothing further to do for renewal. The certificate lands at
`/etc/letsencrypt/live/hackerxploit.org/` - `docker-compose.yml` bind-mounts this
whole path into the `nginx` container read-only, matching what
`nginx/conf.d/default.conf` expects.

---

## Step 4: Build the Frontend

The frontend is a static Vue SPA that Nginx serves directly from
`frontend/dist/` (a bind mount, not a Docker Compose service) - it has to be built
once before the first launch, and rebuilt after any frontend code change.

```bash
cd /opt/hackerxploit/frontend
npm install
npm run build
cd /opt/hackerxploit
```

This produces `frontend/dist/`, ready for Nginx to serve. See "Updating &
Redeploying" below for how to do this again after a frontend change - **never**
`rm -rf dist && mv new_dist dist` while the stack is running (breaks Nginx's bind
mount until restarted, see Troubleshooting item 6). Sync new files into the same
directory (`rsync -a --delete new_build/ frontend/dist/`) or run `npm run build`
directly into `frontend/dist` (the default, as above) and just restart nginx
afterward to be safe.

---

## Step 5: Launch the Stack

```bash
cd /opt/hackerxploit
docker compose up -d --build
```

CTFd's SQLite database lives on the `ctfd_db_data` named volume. Docker creates
brand-new named volumes root-owned, but the CTFd image runs as UID 1001 - on a
truly first-ever run (fresh volume, never used before), CTFd will crash-loop with
`sqlite3.OperationalError: unable to open database file` until this is fixed:

```bash
docker run --rm -v hackerxploit_ctfd_db_data:/var/ctfd_data alpine chown -R 1001:1001 /var/ctfd_data
docker compose up -d ctfd
```

(Replace `hackerxploit_ctfd_db_data` with your actual volume name if the compose
project directory isn't named `hackerxploit` - check with `docker volume ls`. This
step is only needed once, ever, per fresh volume - not on every redeploy.)

Confirm all 8 containers are `Up`:

```bash
docker compose ps
```

---

## Step 6: Seed the Root Admin & Configure CTFd SSO

```bash
# Seeds the platform's root admin account and its OAuth2Client row
docker compose exec web python scripts/init_db.py
```

This prints the root admin's one-time login (`admin` / `HackerXploit`) - log in at
`https://club.hackerxploit.org` and you'll be forced onto a one-time setup screen to
pick a real username/email/password before anything else is usable.

`init_db.py` also tries to push the OAuth config into CTFd's own database, but the
`web` container has no Docker socket access (by design - see Troubleshooting item 7),
so that specific step no-ops with a printed note. Do it as a one-off container
instead, right after:

```bash
docker run --rm \
  --network hackerxploit_default \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$(which docker)":/usr/bin/docker:ro \
  -v /opt/hackerxploit/scripts:/app/scripts:ro \
  --env-file /opt/hackerxploit/.env \
  hackerxploit-web \
  python scripts/init_ctfd.py
```

(Replace `hackerxploit_default` with your actual network name if the compose project
directory isn't named `hackerxploit` - check with `docker network ls`.)

Now visit `https://arena.hackerxploit.org/setup` and complete CTFd's one-time setup
wizard (CTF name, timezone, a local super-admin account - separate from the
platform's SSO, used only for CTFd's own admin panel). Once done, apply the two
functional SSO fixes (relabel the button, hide CTFd's native login form - see
[Feature: CTFd Theme](wiki_repo/Feature-CTFd-Theme.md) for why):

```bash
bash scripts/install-ctfd-theme.sh
```

Cosmetic branding (neon-green CSS + favicon) is a separate opt-in flag, deliberately
not applied by default - CTFd's own admin Theme editor (Config -> Theme) edits the
exact same config keys, so leaving them alone by default means that editor stays
fully usable with nothing to conflict with. Only add branding if you don't plan to
use CTFd's built-in theme editor for anything else:

```bash
bash scripts/install-ctfd-theme.sh --with-branding
```

To actually get the root admin (or any user) recognized as an admin inside CTFd,
sync them once:

```bash
docker compose exec web python -c "
from app import create_app
from app.models import User
from app.services.ctfd_sync import sync_user_to_ctfd
app = create_app()
with app.app_context():
    u = User.query.filter_by(is_root_admin=True).first()
    print(sync_user_to_ctfd(u))
"
```

Every future approval/role-change/suspend/delete syncs to CTFd automatically from
here on (see Troubleshooting item 7 for how this works and how to debug it).

---

## Step 7: DNS - Switch to Cloudflare Proxy (Optional but Recommended)

If you want Cloudflare's CDN/WAF/DDoS protection in front of the site (recommended),
switch the `club` and `arena` A records from "DNS only" to "Proxied" (orange cloud)
in the Cloudflare dashboard, then:

1. Cloudflare dashboard → your zone → **SSL/TLS** → **Overview** → set encryption
   mode to **Full (strict)**. This makes Cloudflare validate the origin's real
   Let's Encrypt certificate on every request instead of talking plaintext HTTP to
   it or skipping validation.
2. Nothing else to configure - `nginx.conf` already has `set_real_ip_from` entries
   for Cloudflare's published IP ranges and `real_ip_header CF-Connecting-IP`, so
   real visitor IPs correctly reach rate-limiting and audit logs even through the
   proxy (see Troubleshooting item 9 if this ever needs re-verifying, e.g. after
   Cloudflare changes their published ranges).

If you'd rather not use the proxy at all, leave both records on "DNS only" -
everything works identically either way, you just lose Cloudflare's edge
protection and CDN caching.

---

## Step 8: Verify Everything

```bash
docker compose ps                                     # all 8 services "Up"
curl -s https://club.hackerxploit.org/api/health       # {"status":"healthy", ...}
curl -sI https://arena.hackerxploit.org/healthcheck    # HTTP/2 200
```

- `https://club.hackerxploit.org` - Club Main App, also hosts login/register/
  forgot-password and the OAuth2/SSO provider.
- `https://arena.hackerxploit.org` - CTFd Platform. Its login page should show a
  "Login with HackerXploit"-labeled SSO button (via the theme installer above) that
  redirects to `club.hackerxploit.org/oauth/authorize`.

---

## Step 9: Take a Baseline Backup

```bash
./scripts/hx-backup.sh backup
```

Covers both the platform database and CTFd's database in one archive. Do this once
right after initial setup, and on whatever cadence makes sense before relying on the
Celery-scheduled snapshots alone.

---

## Step 10: External Uptime Monitoring (Optional)

Configure an external uptime monitor (e.g., UptimeRobot) with HTTP(S) 5-minute
interval checks for both subdomains:

1. **Club Application**: `https://club.hackerxploit.org/api/health` (expects HTTP 200, `{"status": "healthy"}`)
2. **CTFd Competition Platform**: `https://arena.hackerxploit.org/healthcheck` (expects HTTP 200)

---
---

# Updating & Redeploying Code Changes

Once the stack is live, here's how to ship any future code change - backend,
frontend, or infra config - without any AI assistance.

```bash
cd /opt/hackerxploit
git fetch origin
git reset --hard origin/main   # discards nothing of yours: .env and frontend/dist
                                # are both gitignored, never tracked by git
git log --oneline -1           # confirm you're on the commit you expect
```

Then, depending on what changed:

**Backend changed** (`backend/`, `scripts/`, `docker-compose.yml`'s service
definitions):
```bash
docker compose up -d --build web celery_worker celery_beat
```
New database columns/indexes (added to the migration list in
`backend/app/__init__.py`) apply automatically the moment `web` boots - no separate
migration step needed. Check it worked: `docker compose logs web --tail=30`.

**Frontend changed** (`frontend/src/`, anything under `frontend/`):
```bash
cd /opt/hackerxploit/frontend
npm install    # only needed if package.json changed
npm run build  # rebuilds directly into frontend/dist
cd /opt/hackerxploit
docker compose restart nginx   # always do this after any frontend/dist change -
                                # see Troubleshooting item 6 for why
```

**Nginx config changed** (`nginx/nginx.conf`, `nginx/conf.d/*.conf`):
```bash
docker compose exec nginx nginx -t     # validates syntax before touching anything live
docker compose restart nginx
```

**`docker-compose.yml` changed** (new service, new volume, new env var):
```bash
docker compose up -d --build   # rebuilds/recreates whatever actually changed
```

**Verify after any change:**
```bash
docker compose ps                                  # all 8 still "Up", nothing "Restarting"
curl -s https://club.hackerxploit.org/api/health
curl -sI https://arena.hackerxploit.org/healthcheck
```

---
---

# Troubleshooting

Real issues this exact stack has hit in production, and their actual fixes - not
hypothetical ones.

### 1. A container is stuck "Restarting"

```bash
docker compose ps                              # spot the one not "Up"
docker compose logs <service> --tail=50        # read the real traceback
```

Common causes seen in practice:
- **`RuntimeError: Refusing to start in production: X is unset or is a known
  insecure placeholder value`** - a required secret is missing or still a
  placeholder. Check `.env` has a real value, and check `docker-compose.yml`'s
  `environment:` block for that specific service actually passes it through (not
  every var in `.env` is automatically visible to every container - each service
  lists exactly what it receives).
- **`ModuleNotFoundError: No module named 'X'`** - a Python package used by the code
  is missing from `backend/requirements.txt`. Add it (check what version works with
  `pip show X` if you have it installed anywhere else), then
  `docker compose up -d --build web celery_worker celery_beat`.
- **`sqlite3.OperationalError: unable to open database file`** (CTFd specifically) -
  see item 3 below.

### 2. 502 Bad Gateway on club./arena.

Nginx dynamically re-resolves `web`/`ctfd`'s container IP on every request (see
`nginx.conf`'s `resolver` directive), so this shouldn't recur - but if it does:

```bash
docker compose logs nginx --tail=30 | grep -i "connect() failed"
docker compose restart nginx
```

To check whether it's Nginx/origin or something in front of it (e.g. Cloudflare),
test the origin directly, bypassing DNS entirely:
```bash
curl -sSk -H "Host: club.hackerxploit.org" https://<droplet-ip>/api/health
```

### 3. CTFd crash-loops with "unable to open database file"

Only happens on a genuinely fresh `ctfd_db_data` volume (first-ever run, or after
deleting the volume) - Docker creates new named volumes root-owned, but CTFd's
image runs as UID 1001 and can't write there until fixed:

```bash
docker run --rm -v hackerxploit_ctfd_db_data:/var/ctfd_data alpine chown -R 1001:1001 /var/ctfd_data
docker compose up -d ctfd
```

### 4. CTFd theme / SSO button label / OAuth config changes don't appear

CTFd memoizes every config value it reads in Redis (DB 1), and only busts that
cache on writes through its own Python code - not when the row is changed directly
in SQLite, which is all `install-ctfd-theme.sh` and `init_ctfd.py` can do from
outside the container. Both scripts flush this automatically, but if Redis's
password ever changes without updating them, the flush fails silently in older
versions of these scripts (fixed - they now verify the flush actually happened).
Verify directly:

```bash
set -a && source /opt/hackerxploit/.env && set +a
docker exec hx_redis redis-cli -a "$REDIS_PASSWORD" -n 1 DBSIZE   # should read 0 right after a real flush
docker exec hx_redis redis-cli -a "$REDIS_PASSWORD" -n 1 FLUSHDB  # manual flush if needed
```

### 5. Login says "Invalid credentials" but the password should be right

Don't guess - check what the server actually recorded:

```bash
docker compose exec web python -c "
from app import create_app
from app.models import LoginAttempt
app = create_app()
with app.app_context():
    for r in LoginAttempt.query.order_by(LoginAttempt.created_at.desc()).limit(5).all():
        print(r.created_at, r.username_attempted, r.success, r.failure_reason)
"
```

- `failure_reason` = "Incorrect password" -> the username was found, but whatever
  was typed genuinely didn't match. Retype carefully (watch mobile autocapitalize/
  autocorrect on the password field, and trailing spaces from copy-paste).
- Anything mentioning a lockout -> too many recent failed attempts on that account;
  wait 15 minutes, or use the Admin Runbook's account-unlock flow
  (`/admin/security/login-activity` → **Manually Unlock**).

### 6. A frontend deploy leaves the site 403ing with "directory index... is forbidden"

Happens if `frontend/dist/` was replaced as a whole directory (`rm -rf dist && mv
new_dist dist`) while Nginx was running - Nginx's bind mount can end up pointing at
the old, now-gone directory until restarted. Fix:

```bash
docker compose restart nginx
```

Avoid triggering this at all: build straight into `frontend/dist` (the default
output path) or `rsync -a --delete` new files into the existing directory, rather
than swapping the whole directory - and restart nginx after any frontend deploy
regardless, as cheap insurance.

### 7. CTFd account sync (approve / role-change / suspend / delete) doesn't reflect in CTFd

`backend/app/services/ctfd_sync.py` talks **directly to CTFd's SQLite file** via a
Docker volume (`ctfd_db_data`) shared read-write between the `ctfd` and `web`
services - not via `docker exec`, and not via any Docker socket access (the `web`
container deliberately has none, so a compromised app can't reach the host). If
this ever stops working:

```bash
# Confirm the shared volume mount still exists on `web`
grep -A2 "ctfd_db_data:/var/ctfd_data" docker-compose.yml

# Manually test a sync
docker compose exec web python -c "
from app import create_app
from app.models import User
from app.services.ctfd_sync import sync_user_to_ctfd
app = create_app()
with app.app_context():
    u = User.query.filter_by(username='SOME_USERNAME').first()
    print(sync_user_to_ctfd(u))
"

# Confirm it actually landed in CTFd's own database
docker exec hx_ctfd python -c "
import sqlite3
conn = sqlite3.connect('/var/ctfd_data/ctfd.db')
for r in conn.cursor().execute('SELECT id, name, email, type FROM users').fetchall(): print(r)
"
```

### 8. Favicon / static asset looks unchanged after an update

Almost always your browser's own cache, not a server issue - browsers hold onto
favicons especially stubbornly, often ignoring normal cache-control headers.
Verify the server side directly before assuming anything's broken:

```bash
curl -sSk -H "Host: arena.hackerxploit.org" https://<droplet-ip>/themes/core/static/img/favicon.ico | md5sum
md5sum frontend/public/favicon.ico
```

If these match, the server is correct - open the site in a private/incognito window
to confirm, then clear your regular browser's cache.

### 9. An admin-deleted item (announcement, banner, etc.) reappears after a redeploy

This exact bug happened once with the dashboard announcement banner and is fixed,
but if a similar "deleted thing comes back" bug ever appears elsewhere: the root
cause pattern is a startup migration in `backend/app/__init__.py` (they run on every
`web` boot) gated only on "is this table empty?" rather than a persistent "have I
already run?" flag - which can't tell "never run yet" apart from "an admin
deliberately emptied this on purpose." Grep that file for the relevant table/model
name and check whether the guard condition has this flaw.

### 10. SSL certificate

Auto-renews via the systemd timer Certbot installed - `systemctl list-timers | grep
certbot` should show it scheduled. Force a dry-run to confirm it still works:
```bash
certbot renew --dry-run
```
The Cloudflare API token used for DNS-01 validation lives at
`/root/.secrets/cloudflare.ini` - if it's ever revoked/rotated in Cloudflare,
update that file with the new token.

### 11. General health check

```bash
docker compose ps                                     # all 8 should show "Up"
curl -s https://club.hackerxploit.org/api/health       # {"status":"healthy", ...}
curl -sI https://arena.hackerxploit.org/healthcheck    # HTTP/2 200
docker compose logs <service> --tail=50 -f             # live-tail any service's logs
```

### 12. CTFd's "Login with HackerXploit" button says "OAuth token retrieval failure"

Check CTFd's own login log for confirmation: `docker exec hx_ctfd cat
/opt/CTFd/CTFd/logs/logins.log | grep "OAuth token retrieval failure"`. If present,
CTFd's token exchange request to `/oauth/token` is being rejected - inspect
`backend/app/routes/oauth.py`'s `token()` function's checks one at a time; CTFd's
actual token request only ever sends `code`, `client_id`, `client_secret`,
`grant_type` (confirmed from CTFd's own source, `CTFd/auth.py`) - never assume it
sends anything else (e.g. `redirect_uri`), even if the OAuth2 spec allows a server
to expect it.

### 13. A user gets "Your username or password is incorrect" trying to log into CTFd

Ask which login form they used. CTFd shows two: the "Login with HackerXploit" SSO
button (the only one that can ever work - CTFd-provisioned accounts get a random,
never-disclosed password, see `ctfd_sync.py`), and CTFd's own native username/
password form directly below it, which can never succeed for any platform account.
The native form should already be hidden by `scripts/install-ctfd-theme.sh`'s
theme_footer JS - if it's still visible, re-run that script and hard-refresh.

### 14. A user clicks CTFd's SSO button and lands on a raw JSON error instead of the login page

Fixed - `/oauth/authorize` now redirects unauthenticated browsers to `/login` (or
`/setup-admin`/`/onboarding` as appropriate) instead of returning JSON, since this
endpoint is only ever reached via full browser navigation, never an API/fetch call.
If this class of bug ever recurs on a similar full-page-navigation-only endpoint:
check whether it's using a blanket auth decorator built for API/AJAX routes
(JSON error responses) instead of an inline check that redirects.

### 15. Using CTFd's own admin Theme editor "undoes" the SSO/theme customization

`scripts/install-ctfd-theme.sh` writes into `Configs.theme_header`/`theme_footer` -
the exact same two fields CTFd's own admin panel (Config -> Theme -> "Theme Header"/
"Theme Footer") edits directly. By default the script only writes to `theme_footer`
(the SSO button relabel + hidden native-login-form JS), leaving `theme_header`
untouched specifically so that editor stays safe to use for cosmetic changes. If an
admin edits/clears "Theme Footer" in that UI and saves, it will overwrite the SSO
fixes - just re-run `bash scripts/install-ctfd-theme.sh` to reinstall them. Branding
(`--with-branding`) is opt-in for the same reason: don't apply it if you plan to use
CTFd's built-in theme editor for anything.

---
---

# Staging Droplet (Pre-Production Migration Testing)

To test database migrations, dynamic profile schema changes, or breaking updates
prior to production:

1. Spin up a cheap $6/mo DigitalOcean staging droplet (`staging.hackerxploit.org`).
2. Clone repository & configure `.env` pointing to staging URLs:
   ```bash
   SESSION_COOKIE_DOMAIN=.staging.hackerxploit.org
   DOMAIN=staging.hackerxploit.org
   ```
3. Dump production PostgreSQL database schema:
   ```bash
   docker compose exec db pg_dump -U hx_user -d hackerxploit --schema-only > staging_schema.sql
   ```
4. Restore schema on staging droplet and run the verification scripts under `tests/`
   to confirm zero-downtime migration behavior before touching production.
