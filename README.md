# HackerXploit Club Platform 🚀

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/thw01f/HackerXploit)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/thw01f/HackerXploit)
[![Python](https://img.shields.io/badge/Python-3.13-cyan)](https://www.python.org/)
[![Vue 3](https://img.shields.io/badge/Vue.js-3.4-emerald)](https://vuejs.org/)

**HackerXploit Club Platform** is an enterprise-grade cybersecurity club membership, CTF integration, learning management, and communication system designed for university cybersecurity organizations.

---

## 📖 Comprehensive Documentation

> **Complete system documentation, architecture diagrams, database schemas, role matrices, API references, deployment guides, admin runbooks, and feature guides are published in the official GitHub Wiki:**
> 
> 👉 **[Explore the HackerXploit GitHub Wiki](https://github.com/thw01f/HackerXploit/wiki)**

### Quick Documentation Links
- **[Home & Master Index](https://github.com/thw01f/HackerXploit/wiki/Home)**
- **[System Architecture & Subdomains](https://github.com/thw01f/HackerXploit/wiki/Architecture)**
- **[Database Schema Reference](https://github.com/thw01f/HackerXploit/wiki/Database-Schema)**
- **[User Roles & Permissions Matrix](https://github.com/thw01f/HackerXploit/wiki/User-Roles-And-Permissions)**
- **[API & Routes Reference Directory](https://github.com/thw01f/HackerXploit/wiki/API-And-Routes-Reference)**
- **[DigitalOcean Deployment Guide](https://github.com/thw01f/HackerXploit/wiki/Deployment-Guide)**
- **[Admin Operations Runbook](https://github.com/thw01f/HackerXploit/wiki/Admin-Runbook)**
- **[Security Notes & Architecture](https://github.com/thw01f/HackerXploit/wiki/Security-Notes)**

---

## 🛠️ Tech Stack & Technologies

- **Backend**: Python 3.13 Flask (Blueprints), Gunicorn + Gevent workers behind Nginx.
- **Frontend**: Vue 3 SPA, Vue Router, Pinia, Custom Cyberpunk Neon Dark CSS Design System.
- **Database**: PostgreSQL 16 (optimized for concurrent activity tracking).
- **Cache & Real-time**: Redis 7, Flask-SocketIO message queue, Celery worker & beat scheduler.
- **Messaging & Moderation**: Scope-targeted broadcast inbox, text-only chat channel with soft-delete & admin reset, real-time notification drawer, SMTP transactional email relay, and unified content moderation queue.
- **Security**: Argon2id password hashing, ClamAV virus scanning, real-content MIME sniffing (`python-magic`), Pillow image compression, Cloudflare Turnstile CAPTCHA.

---

## 💻 Local Development Setup

```bash
# 1. Clone repository
git clone https://github.com/thw01f/HackerXploit.git
cd HackerXploit

# 2. Configure environment (required — the stack refuses to start without unique secrets)
cp .env.example .env
# Edit .env and replace every REPLACE_WITH_A_UNIQUE_RANDOM_* placeholder.
# Keep POSTGRES_PASSWORD/REDIS_PASSWORD in sync with DATABASE_URL/REDIS_URL.
# For local dev you can set FLASK_ENV=development to skip the production secret checks.

# 3. Setup Virtual Environment & Backend Dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 4. Setup Frontend Dependencies
cd frontend
npm install
cd ..

# 5. Start Docker Services (Postgres & Redis)
docker compose up db redis -d

# 6. Run Database Initialization & Seed Root Admin
PYTHONPATH=backend python scripts/init_db.py

# 7. Run Test Suite
PYTHONPATH=backend pytest tests/ -v
```

For full production deployment instructions on DigitalOcean with Certbot SSL and CTFd SSO, see the **[Deployment Guide](https://github.com/thw01f/HackerXploit/wiki/Deployment-Guide)** on the Wiki.

---

## 📄 License
MIT License. Created for College Cybersecurity Clubs.
