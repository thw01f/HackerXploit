# HackerXploit Club Platform 🚀

**HackerXploit Club Platform** is an enterprise-grade cybersecurity club membership, CTF integration, and learning management system designed for college cybersecurity organizations.

Deployed as a unified single-node Docker Compose stack on DigitalOcean, it seamlessly connects three subdomains behind an Nginx reverse proxy with wildcard SSL certificate support.

---

## 🌐 Subdomain Architecture

- **`hackerxploit.org`**: Public landing & marketing site + Auth Service (OAuth2 Provider, Login, Registration).
- **`club.hackerxploit.org`**: Main Application Portal (Vue 3 SPA with Cyberpunk Digital ID Card, Academy, Competitions, Opportunities, Live Chat).
- **`ctf.hackerxploit.org`**: Official CTFd CTF Platform (configured as OAuth2 Client of Auth Service for shared login SSO across `.hackerxploit.org`).

---

## 🛠️ Stack & Technologies

- **Backend**: Python Flask (Blueprints), Gunicorn + Gevent workers behind Nginx.
- **Frontend**: Vue 3, Vue Router, Pinia, Custom Cyberpunk Neon Dark CSS Design System.
- **Database**: PostgreSQL 16 (optimized for concurrent activity tracking).
- **Cache & Real-time**: Redis 7, Flask-SocketIO message queue, Celery worker & beat scheduler.
- **Security**: Argon2id password hashing, ClamAV virus scanning, real-content MIME sniffing, Pillow image compression, Cloudflare Turnstile CAPTCHA.

---

## 🚀 Quick Start (Docker Compose)

```bash
# 1. Clone repository
git clone https://github.com/thw01f/HackerXploit.git
cd HackerXploit

# 2. Copy environment file
cp .env.example .env

# 3. Start full stack
docker-compose up -d --build

# 4. Initialize Database & Seed OAuth2 Client
docker-compose exec web python /app/../scripts/init_db.py
```

---

## 📚 Documentation Index

- [Architecture Overview](ARCHITECTURE.md)
- [Deployment Guide & DigitalOcean Setup](DEPLOYMENT.md)
- [Security Architecture & Upload Pipeline](SECURITY.md)
- [Role & Permissions Matrix](ROLE_MATRIX.md)
- [Disaster Recovery & Backup Guide](BACKUPS.md)

---

## 📄 License
MIT License. Created for College Cybersecurity Clubs.
