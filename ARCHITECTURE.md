# Technical Architecture

## Overview

The HackerXploit Club Platform operates as a single Docker Compose deployment hosting two subdomains behind an Nginx reverse proxy. `hackerxploit.org` (the bare root domain) is deliberately **not** claimed by this deployment at all — see "Domain Scoping" below.

```
                               ┌─────────────────────────┐
                               │   Nginx Reverse Proxy   │
                               │   Wildcard SSL (*.org)  │
                               └────────────┬────────────┘
                                            │
                        ┌───────────────────────────────┐
                        ▼                               ▼
            ┌───────────────────────┐       ┌───────────────────────┐
            │ club.hackerxploit.org │       │  arena.hackerxploit.org │
            │ Club Portal SPA + Auth │       │    CTFd (OAuth SSO)   │
            └───────────┬───────────┘       └───────────┬───────────┘
                        │                               │
                        └───────────────────────────────┘
                                            │
                               ┌────────────▼────────────┐
                               │     Flask REST API      │
                               │   Gunicorn + Gevent     │
                               └─────┬──────┬──────┬─────┘
                                     │      │      │
           ┌─────────────────────────┘      │      └─────────────────────────┐
           ▼                                ▼                                ▼
┌─────────────────────┐          ┌───────────────────┐          ┌────────────────────────┐
│  PostgreSQL Database │          │    Redis Cache    │          │  Celery Worker & Beat  │
└─────────────────────┘          └───────────────────┘          └────────────────────────┘
```

## Backend Modules & Blueprints

- `auth_bp` (`/api/auth`): Registration, login with 5-attempt lockout, argon2 hashing, session revocation kill-switch.
- `oauth_bp` (`/oauth`): Authlib OAuth2 provider (`/oauth/authorize`, `/oauth/token`, `/oauth/userinfo`) for CTFd SSO.
- `uploads_bp` (`/api/uploads`): Centralized upload pipeline with MIME sniffing, ClamAV virus scanning, WebP conversion, and thumbnail generation.
- `academy_bp` (`/api/academy`): Course creation, module/lesson authoring, enrollment, certificate generation.
- `competition_bp` (`/api/competitions`): Competition creation, admin approval workflow, student application verification, post-event wrap-ups.
- `opportunity_bp` (`/api/opportunities`): Internships, research positions, CTF team recruitment applications.
- `club_bp` (`/api/club`): Member leaderboard, structured student profile tracking, dashboard statistics.
- `admin_bp` (`/api/admin`): Registration approval queue, hard cap of 5 admins enforcement, root admin control, `/admin/security/login-activity` security viewer, audit logs.
- `chat_bp` (`/api/chat`): Real-time multi-channel chat history, teacher soft-delete moderation.

## Session Cookie Scope

All authentication sessions issue HTTP-only cookies scoped to `.club.hackerxploit.org`
(`SESSION_COOKIE_DOMAIN` in `backend/app/config.py`) — not the wildcard
`.hackerxploit.org`. The cookie has no reason to be sent to `arena.hackerxploit.org`
(CTFd runs its own session; it interacts with the club app purely via browser-mediated
OAuth2 redirects and server-to-server token exchange, never by reading this cookie),
and definitely not to the bare `hackerxploit.org` root domain, which this deployment
doesn't touch at all.

## Domain Scoping (as of 2026-08-03)

`hackerxploit.org` (bare root + `www.`) is **reserved for other, unrelated projects**
and is not configured anywhere in this repo's Nginx/Docker Compose setup — no server
block claims it, nothing here serves anything on it. This deployment only owns two
subdomains:

- **`club.hackerxploit.org`** — the entire application: the SPA, every `/api/` route
  (including `/api/auth/*` — register, login, logout, forgot-password, `/me`, etc.),
  the OAuth2/SSO provider (`/oauth/authorize`, `/oauth/token`, `/oauth/userinfo`) that
  CTFd's "Login with HackerXploit" redirects to, `/socket.io/`, and `/uploads/`. There
  is no separate auth subdomain to keep in sync with this one.
- **`arena.hackerxploit.org`** — CTFd, configured as an OAuth2 client pointing at
  `club.hackerxploit.org` for SSO (`scripts/init_ctfd.py`, via the
  `CTFD_OAUTH_PUBLIC_BASE_URL` env var).

Because everything lives on one domain now, `club.hackerxploit.org`'s Nginx `location /`
no longer needs (and no longer has) the old cookie-presence redirect-to-a-separate-
auth-domain check — that pattern would infinite-loop against `/login` itself once
login is served from the same domain it protects. Vue Router's own auth guard
(`frontend/src/App.vue`) already gates every non-public route client-side.

The Certbot wildcard cert (`*.hackerxploit.org` + `hackerxploit.org`, DNS-01 challenge)
is still the simplest way to get valid TLS for both subdomains with one certificate —
this doesn't require this deployment to serve anything on the bare root domain, only
to prove DNS control of it during issuance.
