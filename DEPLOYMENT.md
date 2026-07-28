# Deployment Guide: Single DigitalOcean Droplet

This guide covers deploying the HackerXploit Club Platform on a single DigitalOcean Droplet using Docker Compose and Certbot wildcard SSL certificates.

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
nano .env  # Update SECRET_KEY and DB passwords
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
docker-compose up -d --build

# Run database initialization & seed CTFd OAuth client
docker-compose exec web python /app/../scripts/init_db.py
```

---

## Step 5: Verify Subdomain Health

- `http://hackerxploit.org` (Auth & Marketing)
- `http://club.hackerxploit.org` (Club App)
- `http://ctf.hackerxploit.org` (CTFd Platform)
