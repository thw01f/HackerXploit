#!/usr/bin/env bash
# ============================================================================
# HackerXploit CTFd Theme Installer
#
# Applies the HackerXploit brand (dark/light palette matching the main
# platform - neon green #9fef00, cyan #00f0ff, monospace type) on top of the
# running CTFd container's stock "core" theme, plus a matching favicon.
#
# How it works (no CTFd template files are touched, nothing to break):
#   - CTFd's base.html renders `{{ Configs.theme_header }}` verbatim right
#     before </head>. We set that config value in CTFd's own database to a
#     <style> block with our CSS overrides. CTFd's native light/dark toggle
#     (Bootstrap 5.3's data-bs-theme attribute) is reused as-is - we only
#     override the CSS variables it already reads.
#   - The favicon file CTFd serves by default is overwritten directly (the
#     original is backed up first, on the very first run only).
#
# Usage:
#   ./install-ctfd-theme.sh              # installs against container "hx_ctfd"
#   CTFD_CONTAINER=my_ctfd ./install-ctfd-theme.sh
#
# Safe to re-run - every step is idempotent.
# To revert: ./install-ctfd-theme.sh --uninstall
# ============================================================================
set -euo pipefail

CONTAINER="${CTFD_CONTAINER:-hx_ctfd}"
FAVICON_PATH_IN_CONTAINER="/opt/CTFd/CTFd/themes/core/static/img/favicon.ico"
FAVICON_BACKUP_PATH="/opt/CTFd/CTFd/themes/core/static/img/favicon.ico.hx-original-backup"
CSS_TMP_IN_CONTAINER="/tmp/hackerxploit-ctfd-theme.css"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_FAVICON="${HX_FAVICON_PATH:-$SCRIPT_DIR/../frontend/public/favicon.ico}"

log()  { printf '\033[1;32m[hx-theme]\033[0m %s\n' "$1"; }
warn() { printf '\033[1;33m[hx-theme]\033[0m %s\n' "$1"; }
die()  { printf '\033[1;31m[hx-theme]\033[0m %s\n' "$1" >&2; exit 1; }

require_container() {
  if ! command -v docker >/dev/null 2>&1; then
    die "docker is not installed or not on PATH."
  fi
  if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
    die "Container '$CONTAINER' is not running. Set CTFD_CONTAINER=<name> if it's named differently."
  fi
}

uninstall() {
  require_container
  log "Reverting theme_header config in CTFd..."
  docker exec -i "$CONTAINER" python -c "
import sqlite3
conn = sqlite3.connect('/tmp/ctfd.db')
cur = conn.cursor()
cur.execute(\"DELETE FROM config WHERE key = 'theme_header'\")
conn.commit()
conn.close()
print('[CTFd Theme] theme_header cleared')
"
  log "Restoring original favicon (if a backup exists)..."
  # Run as root: the currently-installed favicon may be owned by a host UID
  # (from `docker cp` during install) that the container's own user can't overwrite.
  docker exec -u root -i "$CONTAINER" sh -c "
    set -e
    if [ -f '$FAVICON_BACKUP_PATH' ]; then
      cp '$FAVICON_BACKUP_PATH' '$FAVICON_PATH_IN_CONTAINER'
      chown ctfd:ctfd '$FAVICON_PATH_IN_CONTAINER'
      echo '[CTFd Theme] favicon restored from backup'
    else
      echo '[CTFd Theme] no favicon backup found, left as-is'
    fi
  "
  log "Theme reverted. Reload CTFd in your browser (hard refresh) to see stock styling again."
  exit 0
}

if [[ "${1:-}" == "--uninstall" ]]; then
  uninstall
fi

require_container

[[ -f "$LOCAL_FAVICON" ]] || die "Favicon not found at $LOCAL_FAVICON (set HX_FAVICON_PATH to override)."

log "Target container: $CONTAINER"

# ---------------------------------------------------------------------------
# 1. Custom CSS -> Configs.theme_header
# ---------------------------------------------------------------------------
log "Writing theme CSS into the container..."
CSS_TMP_LOCAL="$(mktemp)"
trap 'rm -f "$CSS_TMP_LOCAL"' EXIT

cat > "$CSS_TMP_LOCAL" <<'HX_CSS_EOF'
/* ============================================================================
   HackerXploit CTFd Theme
   Matches the main platform's dark/light palette (neon green #9fef00,
   cyan #00f0ff accents, monospace type). Built as a CSS override on top of
   CTFd's stock "core" theme (Bootstrap 5.3) - no template files are touched.
   CTFd's own light/dark toggle (data-bs-theme attribute) is reused as-is.
   ============================================================================ */

:root {
  --bs-body-bg: #f8fafc;
  --bs-body-color: #1e293b;
  --bs-emphasis-color: #0f172a;
  --bs-secondary-color: #475569;
  --bs-primary: #16a34a;
  --bs-primary-rgb: 22, 163, 74;
  --bs-link-color: #0e7490;
  --bs-link-color-rgb: 14, 116, 144;
  --bs-link-hover-color: #155e75;
  --bs-border-color: #e2e8f0;
  --bs-secondary-bg: #ffffff;
  --bs-tertiary-bg: #f1f5f9;
  --hx-accent: #16a34a;
  --hx-accent-cyan: #0e7490;
  --hx-glow: rgba(22, 163, 74, 0.12);
}

[data-bs-theme=dark] {
  --bs-body-bg: #0a0e14;
  --bs-body-color: #cbd5e1;
  --bs-emphasis-color: #f8fafc;
  --bs-secondary-color: #94a3b8;
  --bs-primary: #9fef00;
  --bs-primary-rgb: 159, 239, 0;
  --bs-link-color: #00f0ff;
  --bs-link-color-rgb: 0, 240, 255;
  --bs-link-hover-color: #67f5ff;
  --bs-border-color: #1f293d;
  --bs-secondary-bg: #111927;
  --bs-tertiary-bg: #0c1117;
  --bs-dark: #0a0e14;
  --hx-accent: #9fef00;
  --hx-accent-cyan: #00f0ff;
  --hx-glow: rgba(159, 239, 0, 0.08);
}

body {
  font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  transition: background-color 0.2s ease, color 0.2s ease;
}

h1, h2, h3, h4, h5, h6, .navbar-brand {
  font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-weight: 800;
  letter-spacing: 0.02em;
}

a { color: var(--bs-link-color); }
a:hover { color: var(--bs-link-hover-color); }

/* ---------- Navbar ---------- */
.navbar.bg-dark {
  background-color: #05070b !important;
  border-bottom: 1px solid var(--hx-accent);
  box-shadow: 0 0 20px var(--hx-glow);
}
[data-bs-theme=dark] .navbar.bg-dark {
  background-color: #05070b !important;
}
.navbar-brand {
  color: var(--hx-accent) !important;
  text-transform: uppercase;
  font-weight: 800;
}
.navbar-dark .navbar-nav .nav-link {
  color: rgba(255, 255, 255, 0.75) !important;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.85rem;
}
.navbar-dark .navbar-nav .nav-link:hover,
.navbar-dark .navbar-nav .nav-link.active {
  color: var(--hx-accent) !important;
}

/* ---------- Buttons ---------- */
.btn-primary {
  background-color: var(--hx-accent);
  border-color: var(--hx-accent);
  color: #06120a;
  font-weight: 700;
}
.btn-primary:hover, .btn-primary:focus {
  filter: brightness(1.1);
  background-color: var(--hx-accent);
  border-color: var(--hx-accent);
  color: #06120a;
}
.btn-outline-primary {
  color: var(--hx-accent);
  border-color: var(--hx-accent);
}
.btn-outline-primary:hover {
  background-color: var(--hx-accent);
  color: #06120a;
}
.challenge-button.btn-dark {
  background-color: var(--bs-secondary-bg);
  border: 1px solid var(--bs-border-color);
  transition: all 0.15s ease;
}
.challenge-button.btn-dark:hover {
  border-color: var(--hx-accent);
  box-shadow: 0 0 14px var(--hx-glow);
  transform: translateY(-1px);
}
.challenge-button.solved-challenge {
  border-color: var(--hx-accent) !important;
}

/* ---------- Cards / Modals / Jumbotron ---------- */
.card, .modal-content {
  background-color: var(--bs-secondary-bg);
  border: 1px solid var(--bs-border-color);
}
[data-bs-theme=dark] .card,
[data-bs-theme=dark] .modal-content {
  box-shadow: 0 0 24px rgba(0, 0, 0, 0.4);
}
.jumbotron {
  background-color: var(--bs-tertiary-bg);
  border-bottom: 1px solid var(--bs-border-color);
}

/* ---------- Tables / Scoreboard ---------- */
.table {
  --bs-table-bg: var(--bs-secondary-bg);
  --bs-table-color: var(--bs-body-color);
  --bs-table-striped-bg: var(--bs-tertiary-bg);
  --bs-table-border-color: var(--bs-border-color);
}
.table thead th {
  color: var(--hx-accent);
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.05em;
  border-bottom-width: 2px;
  border-bottom-color: var(--hx-accent) !important;
}
.nav-pills .nav-link.active {
  background-color: var(--hx-accent) !important;
  color: #06120a !important;
  font-weight: 700;
}

/* ---------- Badges ---------- */
.badge.bg-primary { background-color: var(--hx-accent) !important; color: #06120a !important; }
.badge.bg-secondary { background-color: var(--hx-accent-cyan) !important; color: #06120a !important; }

/* ---------- Forms ---------- */
.form-control, .form-select {
  background-color: var(--bs-tertiary-bg);
  border-color: var(--bs-border-color);
  color: var(--bs-body-color);
}
.form-control:focus, .form-select:focus {
  border-color: var(--hx-accent);
  box-shadow: 0 0 0 0.2rem var(--hx-glow);
  background-color: var(--bs-tertiary-bg);
  color: var(--bs-body-color);
}

/* ---------- Alerts ---------- */
.alert-primary, .alert-success {
  background-color: var(--hx-glow);
  border-color: var(--hx-accent);
  color: var(--bs-body-color);
}

/* ---------- Footer ---------- */
.footer {
  border-top: 1px solid var(--bs-border-color);
  background-color: var(--bs-tertiary-bg);
}

/* ---------- Misc polish ---------- */
::selection {
  background: var(--hx-accent);
  color: #06120a;
}
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: var(--bs-tertiary-bg); }
::-webkit-scrollbar-thumb { background: var(--bs-border-color); border-radius: 6px; }
::-webkit-scrollbar-thumb:hover { background: var(--hx-accent); }
HX_CSS_EOF

docker cp "$CSS_TMP_LOCAL" "$CONTAINER:$CSS_TMP_IN_CONTAINER"
# docker cp preserves the host file's numeric UID, which won't match the
# container's runtime user - make it world-readable so the ctfd process can read it back.
docker exec -u root -i "$CONTAINER" chmod 644 "$CSS_TMP_IN_CONTAINER"

docker exec -i "$CONTAINER" python -c "
import sqlite3
conn = sqlite3.connect('/tmp/ctfd.db')
cur = conn.cursor()
with open('$CSS_TMP_IN_CONTAINER', 'r') as f:
    css = f.read()
header_html = '<style id=\"hx-ctfd-theme\">\n' + css + '\n</style>'

cur.execute(\"SELECT id FROM config WHERE key = 'theme_header'\")
row = cur.fetchone()
if row:
    cur.execute('UPDATE config SET value = ? WHERE key = ?', (header_html, 'theme_header'))
else:
    cur.execute('INSERT INTO config (key, value) VALUES (?, ?)', ('theme_header', header_html))
conn.commit()
conn.close()
print('[CTFd Theme] theme_header updated (' + str(len(header_html)) + ' bytes)')
"
docker exec -u root -i "$CONTAINER" rm -f "$CSS_TMP_IN_CONTAINER"

# ---------------------------------------------------------------------------
# 2. Favicon
# ---------------------------------------------------------------------------
log "Installing HackerXploit favicon..."
docker exec -i "$CONTAINER" sh -c "
  if [ ! -f '$FAVICON_BACKUP_PATH' ] && [ -f '$FAVICON_PATH_IN_CONTAINER' ]; then
    cp '$FAVICON_PATH_IN_CONTAINER' '$FAVICON_BACKUP_PATH'
    echo '[CTFd Theme] original favicon backed up'
  fi
"
docker cp "$LOCAL_FAVICON" "$CONTAINER:$FAVICON_PATH_IN_CONTAINER"

log "Done. Hard-refresh CTFd in your browser to see the new theme."
log "To undo everything: $0 --uninstall"
