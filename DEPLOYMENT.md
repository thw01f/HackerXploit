# Deployment Guide: Single DigitalOcean Droplet & Multi-Subdomain Infrastructure

This guide covers deploying the HackerXploit Club Platform on a single DigitalOcean Droplet using Docker Compose, Certbot wildcard SSL certificates, CTFd SSO, and error monitoring.

## Prerequisites

- DigitalOcean Droplet: 4GB RAM / 2 vCPUs minimum recommended (Ubuntu 22.04 LTS).
- Domain registered: `hackerxploit.org`.
- DNS A records set up:
  - `hackerxploit.org` -> Droplet IP
  - `*.hackerxploit.org` -> Droplet IP

---

## Step 1: Install Docker & Docker Compose

```bash
sudo apt update && sudo apt install -y docker.io docker-compose git
sudo systemctl enable --now docker
```

---

## Step 2: Clone & Configure Environment

```bash
git clone https://github.com/thw01f/HackerXploit.git
cd HackerXploit

cp .env.example .env
nano .env  # Update SECRET_KEY, DB passwords, and SENTRY_DSN
```

---

## Step 3: Certbot Wildcard SSL Setup

Generate Let's Encrypt Wildcard SSL for `*.hackerxploit.org` using DNS-01 challenge:

```bash
sudo apt install -y certbot
sudo certbot certonly --manual --preferred-challenges=dns -d hackerxploit.org -d "*.hackerxploit.org"
```

Mount certificates into Nginx container volume in `docker-compose.yml`:
`/etc/letsencrypt:/etc/letsencrypt:ro`

---

## Step 4: Launch Stack & Initialize Database

```bash
docker compose up -d --build

# Run database initialization & seed root admin & CTFd OAuth client
docker compose exec web python scripts/init_db.py
```

---

## Step 5: Verify Subdomain Health & SSO

- `https://hackerxploit.org` (Auth & Marketing)
- `https://club.hackerxploit.org` (Club Main App)
- `https://arena.hackerxploit.org` (CTFd Platform)

Logging in at `hackerxploit.org` persists the `.hackerxploit.org` session cookie, providing seamless access to `club.hackerxploit.org` and single-click SSO into `arena.hackerxploit.org`.

---

## Step 6: External Uptime Monitoring Setup (UptimeRobot)

Configure an external uptime monitor (e.g., UptimeRobot) with HTTP(S) 5-minute interval checks for all three subdomains:

1. **Auth & Public Service**: `https://hackerxploit.org/api/health` (Expects HTTP 200 `{"status": "healthy"}`)
2. **Club Application**: `https://club.hackerxploit.org/api/health` (Expects HTTP 200 `{"status": "healthy"}`)
3. **CTFd Competition Platform**: `https://arena.hackerxploit.org/healthcheck` (Expects HTTP 200 OK)

Configure alerting notifications via Discord Webhook or Email for downtime detection.

---

## Step 7: Staging Droplet Setup (Pre-Production Migration Testing)

To test database migrations, dynamic profile schema changes, or breaking updates prior to production:

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
4. Restore schema on staging droplet and run `flask db upgrade` or verification scripts to confirm zero-downtime migration behavior.
