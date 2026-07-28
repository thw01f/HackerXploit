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
│   hackerxploit.org    │       │ club.hackerxploit.org │       │  ctf.hackerxploit.org │
│  Public Site & Auth   │       │   Club Portal SPA     │       │    CTFd (OAuth SSO)   │
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

All authentication sessions issue HTTP-only cookies scoped to `.hackerxploit.org`. This allows seamless single sign-on across `hackerxploit.org`, `club.hackerxploit.org`, and `ctf.hackerxploit.org`.
