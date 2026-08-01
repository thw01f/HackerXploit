# Security Architecture & Policies

> **See also:** [`SECURITY_AUDIT.md`](SECURITY_AUDIT.md) for the detailed record of the
> 2026-08-01 security audit — every vulnerability found, its impact, and the exact fix
> applied. This document describes the current, post-audit architecture; the audit doc
> is the historical changelog.

## 1. Centralized File Upload Pipeline

Every file upload across the platform (avatars, course attachments, competition certificates, wrap-up photos) is routed through a single pipeline (`UploadPipeline` in `backend/app/services/upload_service.py`).

```
  File Input ──► MIME Sniffing ──► ClamAV Virus Scan ──► Pillow Resize/Compress ──► Storage
                  (Magic Bytes)    (Socket / Daemon)     (WebP & Thumbnails)      (/var/uploads)
```

1. **MIME Sniffing**: Inspects initial byte signatures using `python-magic` to prevent extension-renaming bypasses.
2. **ClamAV Scanning**: Scans stream against ClamAV virus definitions via INSTREAM socket protocol. Fails **closed** in production — if the scanner is unreachable, the upload is rejected rather than silently let through.
3. **Pillow Optimization**: Image files are converted to RGB WebP format, resized if oversized (>1920px), and a thumbnail (200x200) is generated.
4. **Isolated Storage**: Saved under `/var/uploads/<feature>/<uuid>.webp` with randomized UUID filenames to prevent path traversal.

---

## 2. Password Security & Rate Limiting

- **Argon2id Hashing**: Password hashing utilizes `argon2-cffi` (`PasswordHasher`), resisting GPU cracking.
- **Account Auto-Lockout**: 5 consecutive failed login attempts automatically lock the account for 15 minutes.
- **Flask-Limiter + Redis**: Auth endpoints (`/api/auth/login`, `/api/auth/register`) are rate-limited to 5 requests per minute per IP.
- **Cloudflare Turnstile**: Registration and password reset endpoints require Turnstile CAPTCHA verification. The development bypass token only works when `FLASK_ENV != production`; verification fails **closed** if Cloudflare's API is unreachable.

---

## 3. Session Identity & Remote Kill-Switch

- **Cookie-only session identity**: The SPA never reads, stores, or transmits the raw session token itself. Login sets an `HttpOnly`, `Secure` (env-driven), `SameSite=Lax` cookie scoped to `.hackerxploit.org`; every subsequent request (REST and Socket.IO) authenticates via that cookie alone. This closes off session theft via `localStorage`-reading XSS.
- **Hashed server-side lookup**: Sessions are recorded in `device_sessions`, keyed by a SHA-256 hash of the token (`session_token_hash`) — lookups hash the presented cookie value and match against the hash, never the plaintext. Session-listing endpoints (`/api/club/profile/devices`, `/admin/security/sessions`) never return the raw token in their response.
- Users and admins can view active sessions (IP, device user-agent, last active timestamp) and revoke them; revoking invalidates the session server-side immediately.
- **User Suspension**: Suspending a user immediately marks all their active device sessions as inactive, cutting off websocket and REST API access instantly.

---

## 4. Admin Security Log & Visibility

- All authentication attempts (successful or failed) are recorded in `login_activities`.
- **Visibility Restriction**: Access to `/admin/security/login-activity` is strictly restricted to `admin` and `root_admin` roles. Teachers cannot view login activity or security logs — enforced both by endpoint role checks and by `User.to_dict()`, which only includes lockout state (`failed_login_count`, `locked_until`, `is_locked`) when explicitly requested by an admin/root_admin caller (`include_security=True`).

---

## 5. OAuth2 Provider (CTFd SSO)

- `/oauth/token` requires and validates `client_id`/`client_secret` against the registered `OAuth2Client` before issuing tokens, and cross-checks `redirect_uri` against the value used at authorization time. `/oauth/authorize` validates `redirect_uri` against the client's registered URIs before issuing a code. Authorization codes are single-use.
- CTFd-provisioned accounts (`ctfd_sync.py`) each receive a unique, randomly generated password on creation — never a shared or predictable value — since SSO, not local CTFd login, is the intended access path.

---

## 6. Secrets & Network Exposure

- `SECRET_KEY`, the database password, and `CTFD_OAUTH_CLIENT_SECRET` have no usable default in production — the app fails to start if they're unset or match a known placeholder value, and `docker-compose.yml` requires them to be set with no fallback.
- Postgres and Redis are not published to the host network — reachable only from other containers on the compose network. Redis requires a password.
- Database backup archives are stored in a dedicated volume/directory (`BACKUP_FOLDER`) that is never mounted into the nginx container, so they are only reachable through the authenticated `/api/admin/backups/*` endpoints — never directly over HTTP.
