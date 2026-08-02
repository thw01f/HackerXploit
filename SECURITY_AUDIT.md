# Security Audit — August 2026

This document records a security audit of the HackerXploit Club Platform performed on
2026-08-01, the vulnerabilities it found, and the fixes applied in response. It is a
point-in-time record — see git history / `SECURITY.md` for the current state of the
security architecture.

**Scope:** backend (Flask/PostgreSQL/Redis/Celery), frontend (Vue 3 SPA), and
infrastructure (Docker Compose, Nginx, CI/CD). **Method:** manual code review across
three parallel focus areas (backend security, backend architecture/testing,
frontend/infra) followed by targeted remediation and regression testing
(`pytest tests/ -v`, plus a hand-written end-to-end script exercising the OAuth
authorize/token flow).

All items marked **Fixed** below were patched and verified against the full test suite
(36/36 passing) on the `feat/competitions-opportunities-lifecycle` branch. Items marked
**Not yet addressed** are known gaps that were deliberately left out of this pass —
see the note under each.

---

## Critical

### 1. OAuth token endpoint accepted any client without validating `client_secret` or `redirect_uri`
- **File:** `backend/app/routes/oauth.py`
- **Impact:** `/oauth/token` exchanged any valid authorization `code` for access/refresh
  tokens without checking the caller's `client_secret`, and `/oauth/authorize` never
  validated the requested `redirect_uri` against the client's registered URIs. A leaked
  or intercepted authorization code (browser history, referrer leakage, open redirect)
  was sufficient to obtain a full account access token — no client authentication
  required.
- **Fix:** `/oauth/token` now requires `client_id`/`client_secret` and validates them via
  `OAuth2Client.check_client_secret()`; `/oauth/authorize` validates `redirect_uri` via
  `check_redirect_uri()` before issuing a code, and `/oauth/token` re-validates that the
  `redirect_uri` presented at token-exchange matches the one used at authorization time.
  The one-time client "bootstrap" path (auto-registering the CTFd client on first use)
  now only fires for the pre-configured `CTFD_OAUTH_CLIENT_ID` and reads its secret from
  server config — never from request parameters.
- **Status:** Fixed. Verified with a standalone script covering: unknown client rejected,
  mismatched redirect URI rejected, wrong `client_secret` rejected, redirect URI mismatch
  at token exchange rejected, correct flow succeeds, and authorization code reuse is
  rejected (single-use enforced).

### 2. Hardcoded CAPTCHA bypass usable in production
- **File:** `backend/app/utils/captcha.py`
- **Impact:** Submitting the literal string `"DEV_BYPASS_TOKEN"` as the Turnstile token
  bypassed CAPTCHA verification on `/api/auth/register` and password-reset endpoints in
  **any** environment, including production.
- **Fix:** The bypass (and the "dummy secret key" bypass) now only applies when
  `FLASK_ENV != production`. Additionally, Turnstile verification now **fails closed**:
  if Cloudflare's verification API is unreachable, the request is rejected rather than
  silently accepted.
- **Status:** Fixed.

### 3. Every CTFd-provisioned account received an identical, hardcoded password hash
- **File:** `backend/app/services/ctfd_sync.py`
- **Impact:** New CTFd accounts, auto-created on member approval, were all given the same
  static `$bcrypt-sha256$...` password hash. If CTFd's native local-password login was
  ever enabled (not disabled by default), cracking that one hash once would grant login
  access to every member's CTFd account.
- **Fix:** Each new CTFd account now gets its own randomly generated, never-disclosed
  password (hashed with `passlib`'s `bcrypt_sha256` inside the CTFd container at creation
  time). SSO remains the only realistic login path.
- **Status:** Fixed. **Recommendation not yet actioned:** disable CTFd's native local
  login entirely in CTFd's own settings so SSO is enforced structurally, not just by
  password unguessability.

### 4. Database backup archives were served publicly, unauthenticated
- **Files:** `nginx/conf.d/default.conf`, `backend/app/routes/backups.py`,
  `backend/app/config.py`, `docker-compose.yml`
- **Impact:** `backups.py` wrote full database-snapshot ZIP archives (containing every
  `User` row) into `{UPLOAD_FOLDER}/backups/`. Nginx served that entire directory tree
  publicly and unauthenticated at `/uploads/`. Anyone who learned or guessed a backup
  filename (predictable — a UTC timestamp, generated nightly at a fixed time) could
  download the full user database with no login required. It also meant the app's
  separate "gated attachment" mechanism (`/internal_uploads/` + X-Accel-Redirect) gave
  no real protection, since the same files were reachable directly via `/uploads/`.
- **Fix:** Backups now write to a dedicated `BACKUP_FOLDER` (`/var/hx_backups`, backed by
  its own Docker volume `backups_data`) that is mounted only into the `web` and
  `celery_worker` containers — nginx has no access to it at all. All backup
  list/create/delete/download endpoints remain behind `@require_role('admin',
  'root_admin')` as before, but are now the *only* way to reach the files.
- **Status:** Fixed.

### 5. Postgres and Redis exposed directly to the internet, with guessable default credentials
- **Files:** `docker-compose.yml`, `backend/app/config.py`, `.env.example`
- **Impact:** `docker-compose.yml` published Postgres (`5432`) and Redis (`6379`) to the
  host's public network interface. Redis had no password. Postgres's password defaulted
  to a hardcoded, published value (`hx_secure_password_123!`) if the operator's `.env`
  didn't override it. Combined, this was a direct, low-effort path to full database
  compromise on the documented single-droplet production deployment.
- **Fix:**
  - `db` and `redis` no longer publish ports to the host at all (internal Docker network
    only).
  - Redis now requires a password (`--requirepass`, from `REDIS_PASSWORD`).
  - `SECRET_KEY`, the Postgres password (via `DATABASE_URL`), `REDIS_URL`, and
    `CTFD_OAUTH_CLIENT_SECRET` have **no default fallback** in `docker-compose.yml`
    anymore (`${VAR:?must be set}`) — compose refuses to start without them.
  - `backend/app/config.py` additionally fails fast at import time, in production, if
    any of these secrets are unset **or** match one of the placeholder values that used
    to ship in this repo — so even a misconfigured `.env` that forgot one variable can't
    silently boot with a known-insecure default.
  - `.env.example` and `README.md`/`DEPLOYMENT.md` updated accordingly; local dev now
    requires `cp .env.example .env` and filling in real values before `docker compose
    up` will start anything (previously this step was undocumented for local dev).
- **Status:** Fixed.

### 6. Session identity duplicated into a client-readable, localStorage-persisted Bearer token
- **Files:** `frontend/src/stores/auth.js`, `frontend/src/main.js`, `frontend/src/App.vue`,
  `frontend/src/router/index.js`, `frontend/src/services/heartbeat.js`,
  `frontend/src/stores/chat.js`, `backend/app/routes/auth.py`,
  `backend/app/services/socket_events.py`, `nginx/conf.d/default.conf`
- **Impact:** `ARCHITECTURE.md`/`SECURITY.md` describe session identity as living in an
  HttpOnly cookie scoped to `.hackerxploit.org` — and the backend genuinely did set such
  a cookie on login. But the frontend *also* received the raw session token in the login
  JSON response, stored it in `localStorage`, and sent it as a `Bearer` header on every
  request. Any XSS anywhere in the SPA (see also finding #9) could read `localStorage`
  directly and steal a fully live session token — the HttpOnly cookie's protection was
  moot because a parallel, JS-readable copy of the same secret existed. Separately, the
  chat/notifications Socket.IO channel authenticated by having the client send the same
  raw token in a `connect` query parameter and in every `send_message` payload — visible
  in browser devtools network logs and vulnerable to the same theft. The
  `club.hackerxploit.org` nginx "belt-and-suspenders" login gate also checked for a
  cookie named `session=`, which never matched the app's actual cookie name
  (`session_token=`) — effectively dead code.
- **Fix:**
  - The backend no longer returns the raw token in the login JSON body at all — only in
    the HttpOnly, `Secure`-flagged (env-driven), `SameSite=Lax` cookie.
  - The frontend no longer reads, stores, or sends the token anywhere. All auth state is
    derived from `GET /api/auth/me`, called once per page load (tracked via a client-side
    `authChecked` flag) relying solely on the cookie `axios` already sends via
    `withCredentials: true`.
  - Socket.IO now authenticates the same way: at `connect` time the backend reads the
    `session_token` cookie directly (`request.cookies`), resolves the user once, and
    keeps a server-side `sid -> user_id` map for the life of the connection — the client
    never transmits the raw token over the socket at all. (Fixed an adjacent bug in the
    same code path: the online-presence counter never decremented on disconnect.)
  - The nginx cookie-name check was corrected to `session_token=` so the belt-and-
    suspenders redirect actually functions as documented.
- **Status:** Fixed.

---

## High

### 7. Session tokens looked up and stored by plaintext, and leaked via the sessions API
- **Files:** `backend/app/utils/decorators.py`, `backend/app/services/socket_events.py`,
  `backend/app/models/session.py`, `backend/app/routes/auth.py`
- **Impact:** `DeviceSession` already had an unused `session_token_hash` column, but every
  session lookup matched the **plaintext** `session_token` column instead. Worse: both
  `GET /api/club/profile/devices` (a user's own device list) and
  `GET /api/admin/security/sessions` (admin's view of all members' sessions) called
  `DeviceSession.to_dict()`, which serialized the raw, live, usable `session_token` (and
  `session_token_hash`) directly into the JSON response — meaning any authenticated user
  viewing their own device list, or any admin viewing the sessions dashboard, received
  ready-to-use session tokens for every listed device, not just metadata. This is a more
  directly exploitable form of "DB dump hands over live tokens": no DB access was even
  required.
- **Fix:** All lookups (`decorators.py`, `socket_events.py`) now hash the presented token
  (SHA-256) and match against `session_token_hash`. `DeviceSession.to_dict()` no longer
  includes `session_token`/`session_token_hash` in its output at all. Test fixtures across
  6 test files were updated to populate `session_token_hash` (mirroring what the real
  login endpoint already did) so the hashed lookup path is exercised in CI.
- **Status:** Fixed. **Not yet addressed:** the plaintext `session_token` column is still
  written to the database (required by its `NOT NULL`/`unique` constraint and not used
  for authentication anymore) — a full removal would need a proper migration, tracked
  under the broader "adopt Flask-Migrate" architecture item below.

### 8. `SESSION_COOKIE_SECURE` hardcoded off, with no effect from config anyway
- **File:** `backend/app/config.py`, `backend/app/routes/auth.py`
- **Impact:** `SESSION_COOKIE_SECURE = False` was hardcoded with a comment saying to flip
  it in production, but nothing ever did. Separately, the actual session cookie is set
  manually via `resp.set_cookie(...)` in `auth.py`, which doesn't read Flask's
  `SESSION_COOKIE_SECURE` config at all — so even correcting the config value alone would
  not have fixed anything.
- **Fix:** `SESSION_COOKIE_SECURE` is now env-driven, defaulting to `True` when
  `FLASK_ENV=production`. `auth.py`'s manual `set_cookie()` call now explicitly reads
  `SESSION_COOKIE_SECURE`/`SESSION_COOKIE_SAMESITE` from app config.
- **Status:** Fixed.

### 9. Unsanitized markdown rendered via `v-html`
- **File:** `frontend/src/components/InteractiveRoadmapGraph.vue`,
  `backend/app/routes/roadmap.py`
- **Impact:** The roadmap node detail panel ran a hand-rolled regex markdown-to-HTML
  converter client-side, with no sanitization, piped directly into `v-html`. This is
  inconsistent with the rest of the codebase — `CourseDetailView.vue` correctly renders
  `sanitized_html` computed server-side via `markdown_service.py` (Python-Markdown +
  bleach allowlist). Today, roadmap node content is exclusively developer-authored seed
  data (there is no admin/teacher editing endpoint for it yet), so this was not currently
  exploitable by an attacker — but the pattern was a landmine for the first future PR
  that adds an authoring endpoint.
- **Fix:** `GET /api/roadmaps/<slug>` and `PATCH /api/roadmaps/nodes/<id>/progress` now
  compute `description_html` server-side via the existing `render_sanitized_html()`
  helper, matching the Academy convention. The frontend renders that sanitized field via
  `v-html` instead of running its own unsanitized renderer, which was deleted.
- **Status:** Fixed.

### 10. ClamAV scan failures were treated as "clean" (fail open)
- **File:** `backend/app/services/upload_service.py`
- **Impact:** If the ClamAV daemon was unreachable (down, overloaded, network issue), the
  upload pipeline silently treated the file as clean and let it through — an outage of
  the antivirus scanner disabled malware scanning without any visible signal.
- **Fix:** Scanner-unreachable now fails **closed** (upload rejected) when
  `FLASK_ENV=production`. Non-production environments (no ClamAV container running
  locally, as in this repo's test suite and undocumented local-dev flow) still pass
  through, so local development isn't blocked.
- **Status:** Fixed.

### 11. Teachers could see account lockout/security state via student profiles
- **Files:** `backend/app/models/user.py`, `backend/app/routes/club.py`,
  `backend/app/routes/admin.py`
- **Impact:** `User.to_dict()` unconditionally included `failed_login_count`,
  `locked_until`, and `is_locked`, regardless of the `include_private` flag. Both
  `GET /api/club/members` and `GET /api/club/members/<id>` — reachable by `teacher` role,
  not just `admin`/`root_admin` — serialized these fields to any teacher, directly
  contradicting `SECURITY.md`'s stated policy ("Teachers cannot view login activity or
  security logs").
- **Fix:** Added a new `include_security` parameter to `User.to_dict()`, defaulting to
  `False`, gating exactly these three fields. Only genuinely admin/root_admin-gated call
  sites (`GET /api/admin/users` when the caller is an admin, `POST
  /admin/security/login-activity/<id>/unlock`, and the admin branch of
  `GET/POST /api/club/members*`) now pass `include_security=True`.
- **Status:** Fixed.

### 12. Backup "restore" silently did nothing while reporting success
- **File:** `backend/app/routes/backups.py`, `frontend/src/views/AdminBackupsView.vue`
- **Impact:** `POST /api/admin/backups/restore` validated the site-name confirmation,
  read the backup's `manifest.json`, and returned `"System backup restored
  successfully"` — without restoring any database row or file. An operator relying on
  this during a real incident would have a false sense of recovery. (The wiki's
  `Feature-Backup-Restore` page also described this as fully functional — corrected as
  part of this audit, see wiki changes below.)
- **Fix:** Rather than build a "real" automated restore under audit time pressure — which
  would be a genuinely destructive operation on production data, and this archive format
  only snapshots `User`/`AuditLog`/`BackupRecord` as JSON (not a full database dump), so
  an automated restore here would leave every *other* table (courses, competitions, chat,
  etc.) silently out of sync with the "restored" users, arguably worse than doing nothing
  — the endpoint now returns a clear `501 not_implemented` with a pointer to the existing
  manual `pg_dump`/`psql` procedure documented in `BACKUPS.md`, which performs a full,
  consistent restore. This was a deliberate, discussed scope decision, not an oversight.
- **Status:** Fixed (honesty fix). **Not yet addressed:** a real automated restore
  feature, if wanted, deserves its own dedicated design/review/testing pass — not a
  same-day addendum to a security sweep.

---

## Known gaps not addressed in this pass

These were identified during the audit but intentionally left out of this remediation
round (either lower severity, or requiring a larger dedicated effort):

- **No real database migrations.** `backend/app/__init__.py` runs a growing list of raw
  `ALTER TABLE ... ADD COLUMN` statements at every app boot, wrapped in a bare
  `try/except: rollback` that silently swallows all errors. `Flask-Migrate` is a listed
  dependency but unused. Recommend freezing the current ad-hoc list as an Alembic
  baseline migration and requiring `flask db migrate`/`upgrade` for all future schema
  changes.
- **`admin.py` (779 lines, enforces the root-admin/5-admin-cap invariants) and
  `oauth.py` have zero dedicated test coverage.** CI (`.github/workflows/deploy.yml`)
  also only runs one test file (`test_identity_system.py`), not the full `tests/`
  directory, so most of the suite doesn't gate deploys today.
- **CTFd's own database is ephemeral SQLite** (`sqlite:////tmp/ctfd.db`, not on the
  persisted `ctfd_data` volume) — a container recreate wipes all challenge/score history.
  Fixing this requires coordinating a path change with `ctfd_sync.py`'s hardcoded
  `/tmp/ctfd.db` references, deferred to avoid breaking CTFd sync mid-audit.
- **The roadmap progress-tracking feature appears non-functional.**
  `backend/app/routes/roadmap.py` authenticates via Flask's built-in `session['user_id']`,
  which nothing in this app ever populates (real auth uses the `session_token`
  cookie / `g.current_user`, wired through `require_auth`). As written,
  `PATCH /api/roadmaps/nodes/<id>/progress` likely always returns 401, and
  `GET /api/roadmaps/<slug>` likely never returns per-user progress. This is a functional
  bug, not flagged as a vulnerability, discovered as a side effect of the sanitization
  fix (#9) above.
- **No CSP header, no edge-level (nginx) rate limiting**, unpinned `clamav:latest` /
  `ctfd:latest` Docker images, no staging deploy gate, inconsistent hard-delete vs.
  soft-delete conventions, free-text status/role columns instead of enums, and ~547
  SQLAlchemy/`datetime.utcnow()` deprecation warnings across the codebase.
- **Documentation-vs-reality gap found in the wiki**: `Feature-Security.md` states upload
  volumes are mounted with `noexec` flags in Docker Compose; no such flag exists in
  `docker-compose.yml` today. Corrected in the wiki update accompanying this audit, but
  the control itself (`noexec` mount) has not been implemented.

---

## Verification

- Full backend test suite: `PYTHONPATH=backend pytest tests/ -v` — **36 passed, 0
  failed** after every fix in this document, run repeatedly through the remediation
  process.
- OAuth flow (#1): verified with a temporary standalone script exercising the Flask test
  client against `/oauth/authorize` and `/oauth/token` directly — unknown client
  rejected, bad redirect URI rejected, wrong client secret rejected (401), redirect URI
  mismatch at exchange rejected (400), correct exchange succeeds (200) and issues a
  usable token, code reuse rejected (400), `/oauth/userinfo` accepts the issued token.
- Frontend build: `npm run build` — all 1,834 modules transformed without error (the
  build's final `emptyDir` step failed on a pre-existing local filesystem permission
  issue unrelated to any change here).
