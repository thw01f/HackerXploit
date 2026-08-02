#!/usr/bin/env bash
# ============================================================================
# HackerXploit Unified Backup & Restore
#
# Takes ONE consistent backup covering both systems in this deployment:
#   - The platform's PostgreSQL database (full pg_dump, not a partial snapshot)
#   - CTFd's SQLite database (safe online .backup(), not a raw file copy)
#   - The platform's uploaded files
#   - CTFd's uploaded files
# ...bundled into a single archive, registered in the platform's existing
# `backups` table so it shows up in the admin Backups UI alongside the
# built-in scheduled backups - "one place" to find and manage every backup.
#
# Works whether the app is running containerized (real docker-compose
# production) or host-run (this dev sandbox): it auto-detects whether
# hx_web is a running container and falls back to reading UPLOAD_FOLDER/
# BACKUP_FOLDER as plain host paths otherwise.
#
# Usage:
#   ./hx-backup.sh backup                 # take a full backup now
#   ./hx-backup.sh list                   # list available backups
#   ./hx-backup.sh restore <filename>      # restore from a backup (destructive)
#   ./hx-backup.sh restore <filename> --yes   # skip interactive confirmation
#
# Env overrides: POSTGRES_CONTAINER, CTFD_CONTAINER, WEB_CONTAINER,
#                CELERY_CONTAINER, ENV_FILE (defaults to ./.env)
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="${ENV_FILE:-$REPO_ROOT/.env}"

POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-hx_postgres}"
CTFD_CONTAINER="${CTFD_CONTAINER:-hx_ctfd}"
WEB_CONTAINER="${WEB_CONTAINER:-hx_web}"
CELERY_CONTAINER="${CELERY_CONTAINER:-hx_celery_worker}"
CTFD_UPLOAD_PATH="/var/uploads/ctfd"

log()  { printf '\033[1;32m[hx-backup]\033[0m %s\n' "$1"; }
warn() { printf '\033[1;33m[hx-backup]\033[0m %s\n' "$1"; }
die()  { printf '\033[1;31m[hx-backup]\033[0m %s\n' "$1" >&2; exit 1; }

env_get() {
  # Reads KEY=value out of .env without sourcing the whole file (avoids
  # executing arbitrary content if the file ever contains shell-unsafe values).
  local key="$1" default="${2:-}"
  local val
  val="$(grep -E "^${key}=" "$ENV_FILE" 2>/dev/null | tail -n1 | cut -d= -f2-)"
  echo "${val:-$default}"
}

POSTGRES_DB="$(env_get POSTGRES_DB hackerxploit)"
POSTGRES_USER="$(env_get POSTGRES_USER hx_user)"
POSTGRES_PASSWORD="$(env_get POSTGRES_PASSWORD)"
UPLOAD_FOLDER="$(env_get UPLOAD_FOLDER /var/uploads)"
BACKUP_FOLDER="$(env_get BACKUP_FOLDER /var/hx_backups)"

[[ -n "$POSTGRES_PASSWORD" ]] || die "POSTGRES_PASSWORD not found in $ENV_FILE (set ENV_FILE=/path/to/.env to override)."

require_container() {
  docker ps --format '{{.Names}}' | grep -qx "$1"
}

require_docker() {
  command -v docker >/dev/null 2>&1 || die "docker is not installed or not on PATH."
  require_container "$POSTGRES_CONTAINER" || die "Container '$POSTGRES_CONTAINER' is not running."
  require_container "$CTFD_CONTAINER" || die "Container '$CTFD_CONTAINER' is not running."
}

sha256_of() { sha256sum "$1" | cut -d' ' -f1; }

# ---------------------------------------------------------------------------
# BACKUP
# ---------------------------------------------------------------------------
cmd_backup() {
  require_docker
  # workdir is deliberately not `local`: the EXIT trap below fires after this
  # function returns (at actual script exit), by which point a local variable
  # would already be out of scope and unbound under `set -u`.
  local timestamp archive_name
  timestamp="$(date -u +%Y%m%d_%H%M%S)"
  archive_name="hx_full_backup_${timestamp}.tar.gz"
  workdir="$(mktemp -d)"
  trap 'rm -rf "$workdir"' EXIT

  log "Working directory: $workdir"

  # 1. Platform PostgreSQL - full logical dump, self-cleaning on restore
  log "Dumping platform PostgreSQL database ($POSTGRES_DB)..."
  docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" "$POSTGRES_CONTAINER" \
    pg_dump -U "$POSTGRES_USER" --clean --if-exists -F p "$POSTGRES_DB" > "$workdir/platform_db.sql"

  # 2. CTFd SQLite - consistent online backup (not a raw file copy, which
  #    could grab a half-written page while CTFd is actively writing to it)
  log "Snapshotting CTFd SQLite database..."
  docker exec -i "$CTFD_CONTAINER" python -c "
import sqlite3
src = sqlite3.connect('/tmp/ctfd.db')
dst = sqlite3.connect('/tmp/hx_backup_snapshot.db')
with dst:
    src.backup(dst)
src.close()
dst.close()
"
  docker cp "$CTFD_CONTAINER:/tmp/hx_backup_snapshot.db" "$workdir/ctfd_db.sqlite"
  docker exec "$CTFD_CONTAINER" rm -f /tmp/hx_backup_snapshot.db

  # 3. Platform uploads
  log "Archiving platform uploads..."
  if require_container "$WEB_CONTAINER"; then
    docker cp "$WEB_CONTAINER:$UPLOAD_FOLDER" "$workdir/platform_uploads" 2>/dev/null || mkdir -p "$workdir/platform_uploads"
  elif [[ -d "$UPLOAD_FOLDER" ]]; then
    cp -a "$UPLOAD_FOLDER" "$workdir/platform_uploads"
  else
    mkdir -p "$workdir/platform_uploads"
  fi
  tar czf "$workdir/platform_uploads.tar.gz" -C "$workdir" platform_uploads
  rm -rf "$workdir/platform_uploads"

  # 4. CTFd uploads
  log "Archiving CTFd uploads..."
  docker cp "$CTFD_CONTAINER:$CTFD_UPLOAD_PATH" "$workdir/ctfd_uploads" 2>/dev/null || mkdir -p "$workdir/ctfd_uploads"
  tar czf "$workdir/ctfd_uploads.tar.gz" -C "$workdir" ctfd_uploads
  rm -rf "$workdir/ctfd_uploads"

  # 5. Manifest
  cat > "$workdir/manifest.json" <<EOF
{
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "type": "full",
  "components": ["platform_db.sql", "ctfd_db.sqlite", "platform_uploads.tar.gz", "ctfd_uploads.tar.gz"],
  "postgres_db": "$POSTGRES_DB"
}
EOF

  # 6. Bundle everything into one archive
  log "Bundling final archive..."
  tar czf "$workdir/$archive_name" -C "$workdir" manifest.json platform_db.sql ctfd_db.sqlite platform_uploads.tar.gz ctfd_uploads.tar.gz
  local size_bytes checksum
  size_bytes="$(stat -c%s "$workdir/$archive_name" 2>/dev/null || stat -f%z "$workdir/$archive_name")"
  checksum="$(sha256_of "$workdir/$archive_name")"

  # 7. Land it in the same place the built-in backup feature already uses
  local storage_location
  if require_container "$WEB_CONTAINER"; then
    docker exec "$WEB_CONTAINER" mkdir -p "$BACKUP_FOLDER"
    docker cp "$workdir/$archive_name" "$WEB_CONTAINER:$BACKUP_FOLDER/$archive_name"
    storage_location="$BACKUP_FOLDER (inside $WEB_CONTAINER)"
  else
    mkdir -p "$BACKUP_FOLDER"
    cp "$workdir/$archive_name" "$BACKUP_FOLDER/$archive_name"
    storage_location="$BACKUP_FOLDER (host)"
  fi

  # 8. Register it in the `backups` table so the admin UI lists it too
  log "Registering backup record..."
  docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" -i "$POSTGRES_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 <<SQL
INSERT INTO backups (filename, size_bytes, created_by_id, created_at, type)
VALUES ('$archive_name', $size_bytes, NULL, NOW(), 'full');
SQL

  log "Backup complete: $archive_name ($size_bytes bytes, sha256 $checksum)"
  log "Stored in: $storage_location"
  log "To restore: $0 restore $archive_name"
}

# ---------------------------------------------------------------------------
# LIST
# ---------------------------------------------------------------------------
cmd_list() {
  require_docker
  docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" -i "$POSTGRES_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    -c "SELECT id, filename, type, pg_size_pretty(size_bytes) AS size, created_at FROM backups ORDER BY created_at DESC;"
}

# ---------------------------------------------------------------------------
# RESTORE
# ---------------------------------------------------------------------------
cmd_restore() {
  local filename="${1:-}"
  local auto_yes="${2:-}"
  [[ -n "$filename" ]] || die "Usage: $0 restore <filename> [--yes]"

  require_docker

  # workdir is deliberately not `local` - see the note in cmd_backup().
  workdir="$(mktemp -d)"
  trap 'rm -rf "$workdir"' EXIT

  log "Locating $filename..."
  if require_container "$WEB_CONTAINER"; then
    docker cp "$WEB_CONTAINER:$BACKUP_FOLDER/$filename" "$workdir/$filename" 2>/dev/null \
      || die "Backup '$filename' not found in $WEB_CONTAINER:$BACKUP_FOLDER"
  elif [[ -f "$BACKUP_FOLDER/$filename" ]]; then
    cp "$BACKUP_FOLDER/$filename" "$workdir/$filename"
  else
    die "Backup '$filename' not found in $BACKUP_FOLDER"
  fi

  tar xzf "$workdir/$filename" -C "$workdir"
  [[ -f "$workdir/manifest.json" ]] || die "Archive is missing manifest.json - refusing to restore an unrecognized bundle."

  echo
  warn "=========================================================================="
  warn " THIS WILL PERMANENTLY OVERWRITE the current platform database, CTFd"
  warn " database, and both uploads directories with the contents of:"
  warn "   $filename"
  cat "$workdir/manifest.json"
  warn "=========================================================================="
  echo

  if [[ "$auto_yes" != "--yes" ]]; then
    read -r -p "Type RESTORE to proceed: " confirm
    [[ "$confirm" == "RESTORE" ]] || die "Restore cancelled."
  fi

  # Stop app containers if present so no requests hit a mid-restore DB/files
  local stopped_web=0 stopped_celery=0
  if require_container "$WEB_CONTAINER"; then
    log "Stopping $WEB_CONTAINER for the duration of the restore..."
    docker stop "$WEB_CONTAINER" >/dev/null
    stopped_web=1
  fi
  if require_container "$CELERY_CONTAINER"; then
    log "Stopping $CELERY_CONTAINER for the duration of the restore..."
    docker stop "$CELERY_CONTAINER" >/dev/null
    stopped_celery=1
  fi

  log "Restoring platform PostgreSQL database..."
  docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" -i "$POSTGRES_CONTAINER" \
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 < "$workdir/platform_db.sql"

  log "Restoring CTFd SQLite database..."
  docker cp "$workdir/ctfd_db.sqlite" "$CTFD_CONTAINER:/tmp/ctfd.db"
  # docker cp preserves the host file's numeric UID, which the container's
  # own ctfd user doesn't own - CTFd would boot, serve a few requests, then
  # crash-loop on its first database write ("attempt to write a readonly
  # database"). Fix ownership before restarting, while the (still-running,
  # pre-restart) container lets us exec as root.
  docker exec -u root "$CTFD_CONTAINER" chown ctfd:ctfd /tmp/ctfd.db
  docker exec -u root "$CTFD_CONTAINER" chmod 644 /tmp/ctfd.db
  docker restart "$CTFD_CONTAINER" >/dev/null

  log "Restoring platform uploads..."
  tar xzf "$workdir/platform_uploads.tar.gz" -C "$workdir"
  # docker cp works against a stopped container too (no exec/running requirement),
  # so this covers the case where we just stopped hx_web above.
  if docker ps -a --format '{{.Names}}' | grep -qx "$WEB_CONTAINER"; then
    docker cp "$workdir/platform_uploads/." "$WEB_CONTAINER:$UPLOAD_FOLDER" 2>/dev/null || true
  else
    mkdir -p "$UPLOAD_FOLDER"
    rm -rf "${UPLOAD_FOLDER:?}"/* 2>/dev/null || true
    cp -a "$workdir/platform_uploads/." "$UPLOAD_FOLDER/"
  fi

  log "Restoring CTFd uploads..."
  tar xzf "$workdir/ctfd_uploads.tar.gz" -C "$workdir"
  docker cp "$workdir/ctfd_uploads/." "$CTFD_CONTAINER:$CTFD_UPLOAD_PATH"
  docker exec -u root "$CTFD_CONTAINER" chown -R ctfd:ctfd "$CTFD_UPLOAD_PATH" 2>/dev/null || true

  log "Logging the restore and re-registering this backup..."
  # A backup's own database snapshot is always taken *before* its BackupRecord
  # row is inserted (its filename/size aren't known until the archive is
  # already built) - so restoring from it always "forgets" that backup (and
  # any taken after it). Re-insert it here so the admin UI's Backups list
  # still shows the backup that's currently active, post-restore.
  local restored_size
  restored_size="$(stat -c%s "$workdir/$filename" 2>/dev/null || stat -f%z "$workdir/$filename")"
  docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" -i "$POSTGRES_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 <<SQL
INSERT INTO backups (filename, size_bytes, created_by_id, created_at, type)
VALUES ('$filename', $restored_size, NULL, NOW(), 'full')
ON CONFLICT DO NOTHING;

INSERT INTO audit_logs (actor_name, actor_role, action, notes, created_at)
VALUES ('CLI Restore Script', 'system', 'BACKUP_RESTORED', 'Restored from $filename via hx-backup.sh', NOW());
SQL

  if [[ $stopped_web -eq 1 ]]; then
    log "Restarting $WEB_CONTAINER..."
    docker start "$WEB_CONTAINER" >/dev/null
  fi
  if [[ $stopped_celery -eq 1 ]]; then
    log "Restarting $CELERY_CONTAINER..."
    docker start "$CELERY_CONTAINER" >/dev/null
  fi

  log "Restore complete."
}

case "${1:-}" in
  backup) cmd_backup ;;
  list) cmd_list ;;
  restore) cmd_restore "${2:-}" "${3:-}" ;;
  *) die "Usage: $0 {backup|list|restore <filename> [--yes]}" ;;
esac
