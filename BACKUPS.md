# Disaster Recovery & Backup Guide

This document outlines backup procedures, Celery beat scheduled backups, and disaster recovery commands for the HackerXploit platform.

---

## 0. Unified Backup & Restore (Recommended)

`scripts/hx-backup.sh` takes one consistent backup covering **both** the platform and CTFd in a single archive, and can restore either back to that point in time:

- Platform PostgreSQL database (full `pg_dump --clean`, not a partial snapshot)
- CTFd's SQLite database (safe online backup, not a raw file copy)
- Platform uploads (`UPLOAD_FOLDER`)
- CTFd uploads

```bash
./scripts/hx-backup.sh backup                        # take a full backup now
./scripts/hx-backup.sh list                           # list available backups
./scripts/hx-backup.sh restore <filename>              # restore (destructive - stops app containers, prompts for confirmation)
./scripts/hx-backup.sh restore <filename> --yes        # same, non-interactive
```

Every backup taken this way is registered in the platform's own `backups` table, so it shows up in the admin Backups UI (list/download/delete) alongside the legacy scheduled backups described below. The admin UI's "Restore" button on one of these still points back to this script rather than running in-process, since restoring stops and restarts the web/CTFd/worker containers - something the API process handling that request can't safely do to itself.

Run it from the host (or wherever `docker` is available against this compose project) - it auto-detects whether `hx_web`/`hx_ctfd` are running as containers and falls back to plain host paths for `UPLOAD_FOLDER`/`BACKUP_FOLDER` otherwise (e.g. this dev sandbox, where the app runs outside Docker).

---

## 1. Automated Celery Beat Backups

The `celery_beat` container triggers automated daily PostgreSQL database backups at midnight (`00:00 UTC`):

- Task: `app.services.celery_tasks.perform_database_backup`
- Records audit snapshot in database and writes log entry.

---

## 2. Manual PostgreSQL Database Backup & Restore

### Manual Database Dump

```bash
docker-compose exec -T db pg_dump -U hx_user hackerxploit > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Database Restore Procedure

```bash
# 1. Stop web application
docker-compose stop web celery_worker celery_beat

# 2. Restore database dump
cat backup_YYYYMMDD_HHMMSS.sql | docker-compose exec -T db psql -U hx_user -d hackerxploit

# 3. Restart application containers
docker-compose start web celery_worker celery_beat
```

---

## 3. Upload Volume Backup

The `/var/uploads` directory contains user avatars, course attachments, and competition certificates:

```bash
# Archive uploads volume
tar -cvzf uploads_backup_$(date +%Y%m%d).tar.gz /var/uploads
```
