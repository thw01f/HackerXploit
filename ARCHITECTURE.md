# Technical Architecture

## Overview

The HackerXploit Club Platform operates as a single Docker Compose deployment hosting three distinct subdomains behind an Nginx reverse proxy.

```
                               ┌─────────────────────────┐
                               │   Nginx Reverse Proxy   │
                               │   Wildcard SSL (*.org)  │
                               └────────────┬────────────┘
                                            │
            ┌───────────────────────────────┼───────────────────────────────┐
            ▼                               ▼                               ▼
┌───────────────────────┐       ┌───────────────────────┐       ┌───────────────────────┐
│   hackerxploit.org    │       │ club.hackerxploit.org │       │  arena.hackerxploit.org │
│ Shared Auth Only (SSO)│       │   Club Portal SPA     │       │    CTFd (OAuth SSO)   │
└───────────┬───────────┘       └───────────┬───────────┘       └───────────┬───────────┘
            │                               │                               │
            └───────────────────────────────┼───────────────────────────────┘
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

## Shared SSO Cookie Scope

All authentication sessions issue HTTP-only cookies scoped to `.hackerxploit.org`. This allows seamless single sign-on across `hackerxploit.org`, `club.hackerxploit.org`, and `arena.hackerxploit.org`.

## Domain Scoping (as of 2026-08-03)

`hackerxploit.org` (bare root + `www.`) is reserved for other future use (a separate
site/landing page) and intentionally serves **nothing of the club app itself** — it
exists solely as the shared OAuth2/SSO + login entry point. Nginx (`nginx/conf.d/default.conf`)
only proxies two location blocks on that domain:

- `/oauth/` — the Authlib OAuth2 provider (`/oauth/authorize`, `/oauth/token`, `/oauth/userinfo`) used by CTFd's SSO.
- `/api/auth/` — the `auth_bp` blueprint (register, login, logout, forgot-password, `/me`, etc.) — every route this blueprint exposes and nothing more.

The frontend SPA build is still served at `/` on this domain purely so `/login`,
`/register`, `/forgot-password`, `/onboarding`, and `/setup-admin` render as pages —
Vue Router's own auth guard prevents anything else from doing anything useful even if
visited directly, since none of those other pages' data-fetching calls (`/api/club/...`,
`/api/academy/...`, etc.) are reachable on this domain. `/uploads/` and every other
`/api/` route live exclusively on `club.hackerxploit.org`, which is the actual
application portal.
