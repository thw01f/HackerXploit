# Security Architecture & Policies

## 1. Centralized File Upload Pipeline

Every file upload across the platform (avatars, course attachments, competition certificates, wrap-up photos) is routed through a single pipeline (`UploadPipeline` in `backend/app/services/upload_service.py`).

```
  File Input ──► MIME Sniffing ──► ClamAV Virus Scan ──► Pillow Resize/Compress ──► Storage
                  (Magic Bytes)    (Socket / Daemon)     (WebP & Thumbnails)      (/var/uploads)
```

1. **MIME Sniffing**: Inspects initial byte signatures using `python-magic` to prevent extension-renaming bypasses.
2. **ClamAV Scanning**: Scans stream against ClamAV virus definitions via INSTREAM socket protocol.
3. **Pillow Optimization**: Image files are converted to RGB WebP format, resized if oversized (>1920px), and a thumbnail (200x200) is generated.
4. **Isolated Storage**: Saved under `/var/uploads/<feature>/<uuid>.webp` with randomized UUID filenames to prevent path traversal.

---

## 2. Password Security & Rate Limiting

- **Argon2id Hashing**: Password hashing utilizes `argon2-cffi` (`PasswordHasher`), resisting GPU cracking.
- **Account Auto-Lockout**: 5 consecutive failed login attempts automatically lock the account for 15 minutes.
- **Flask-Limiter + Redis**: Auth endpoints (`/api/auth/login`, `/api/auth/register`) are rate-limited to 5 requests per minute per IP.
- **Cloudflare Turnstile**: Registration and password reset endpoints require Turnstile CAPTCHA verification.

---

## 3. Remote Session Kill-Switch

- All device sessions are recorded in `device_sessions`.
- Users and admins can view active sessions (IP, device user-agent, last active timestamp).
- Revoking a session invalidates the `session_token` server-side immediately.
- **User Suspension**: Suspending a user immediately marks all their active device sessions as inactive, cutting off websocket and REST API access instantly.

---

## 4. Admin Security Log & Visibility

- All authentication attempts (successful or failed) are recorded in `login_activities`.
- **Visibility Restriction**: Access to `/admin/security/login-activity` is strictly restricted to `admin` and `root_admin` roles. Teachers cannot view login activity or security logs.
