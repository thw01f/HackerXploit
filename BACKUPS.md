# Disaster Recovery & Backup Guide

This document outlines backup procedures, Celery beat scheduled backups, and disaster recovery commands for the HackerXploit platform.

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
