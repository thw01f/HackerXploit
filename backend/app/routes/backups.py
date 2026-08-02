import os
import json
import hashlib
import zipfile
import tarfile
from datetime import datetime
from flask import Blueprint, request, jsonify, g, current_app, send_file
from app.models import db, BackupRecord, User, AuditLog
from app.utils.decorators import require_auth, require_role, log_audit

backups_bp = Blueprint('backups', __name__, url_prefix='/api/admin/backups')

def compute_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_backup_dir():
    backup_dir = current_app.config.get('BACKUP_FOLDER', '/var/backups') if current_app else '/var/backups'
    try:
        os.makedirs(backup_dir, exist_ok=True)
    except (PermissionError, OSError):
        backup_dir = "/tmp/hx_backups"
        os.makedirs(backup_dir, exist_ok=True)
    return backup_dir

def create_backup_archive(created_by_id=None, backup_type='manual'):
    base_upload = current_app.config.get('UPLOAD_FOLDER', '/var/uploads') if current_app else '/var/uploads'
    backup_dir = get_backup_dir()

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"hackerxploit_backup_{timestamp}.zip"
    zip_path = os.path.join(backup_dir, filename)

    # Dump Database tables as JSON manifest snapshot
    metadata = {}
    tables = [User, BackupRecord, AuditLog]
    for model in tables:
        try:
            records = model.query.all()
            metadata[model.__tablename__] = [r.to_dict() for r in records if hasattr(r, 'to_dict')]
        except Exception:
            pass

    manifest = {
        'timestamp': datetime.utcnow().isoformat(),
        'type': backup_type,
        'created_by_id': created_by_id,
        'platform_version': '1.0.0',
        'records_count': {k: len(v) for k, v in metadata.items()}
    }

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('manifest.json', json.dumps(manifest, indent=2))
        zf.writestr('database_snapshot.json', json.dumps(metadata, indent=2))

        # Backup media uploads directory if exists
        if os.path.exists(base_upload):
            for root, dirs, files in os.walk(base_upload):
                if 'backups' in root:
                    continue # Do not recursively backup existing backups!
                for file in files:
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, base_upload)
                    zf.write(full_p, arcname=os.path.join('uploads', rel_p))

    size_bytes = os.path.getsize(zip_path)
    checksum = compute_sha256(zip_path)

    # Insert BackupRecord
    record = BackupRecord(
        filename=filename,
        size_bytes=size_bytes,
        created_by_id=created_by_id,
        created_at=datetime.utcnow(),
        type=backup_type
    )
    db.session.add(record)
    db.session.commit()

    return record, checksum

@backups_bp.route('', methods=['GET'])
@require_role('admin', 'root_admin')
def list_backups():
    records = BackupRecord.query.order_by(BackupRecord.created_at.desc()).all()
    return jsonify({
        'backups': [r.to_dict() for r in records]
    }), 200

@backups_bp.route('/create', methods=['POST'])
@require_role('admin', 'root_admin')
def trigger_manual_backup():
    record, checksum = create_backup_archive(created_by_id=g.current_user.id, backup_type='manual')
    log_audit('MANUAL_BACKUP_CREATED', target_type='BackupRecord', target_id=record.id, notes=f"File: {record.filename}")
    return jsonify({
        'message': 'Backup created successfully',
        'backup': record.to_dict(),
        'sha256_checksum': checksum
    }), 201

@backups_bp.route('/<int:backup_id>', methods=['DELETE'])
@require_role('admin', 'root_admin')
def delete_backup(backup_id):
    record = BackupRecord.query.get_or_404(backup_id)

    zip_path = os.path.join(get_backup_dir(), record.filename)
    if os.path.exists(zip_path):
        try:
            os.remove(zip_path)
        except OSError:
            pass

    db.session.delete(record)
    db.session.commit()
    log_audit('BACKUP_DELETED', target_type='BackupRecord', target_id=backup_id)
    return jsonify({'message': 'Backup record and archive file deleted successfully'}), 200

@backups_bp.route('/<int:backup_id>/download', methods=['GET'])
@require_role('admin', 'root_admin')
def download_backup(backup_id):
    record = BackupRecord.query.get_or_404(backup_id)

    zip_path = os.path.join(get_backup_dir(), record.filename)
    if not os.path.exists(zip_path):
        return jsonify({'error': 'Backup archive file not found on disk'}), 404

    return send_file(zip_path, as_attachment=True, download_name=record.filename)

@backups_bp.route('/restore', methods=['POST'])
@require_role('root_admin')
def restore_backup():
    data = request.get_json(silent=True) or {}
    site_confirmation = data.get('site_name', '').strip()
    backup_id = data.get('backup_id')

    if site_confirmation != 'HackerXploit':
        return jsonify({'error': 'Invalid confirmation! You must type exact site name "HackerXploit" to restore.'}), 400

    record = BackupRecord.query.get_or_404(backup_id)
    archive_path = os.path.join(get_backup_dir(), record.filename)

    if not os.path.exists(archive_path):
        return jsonify({'error': 'Backup file missing on server'}), 404

    # Full backups (scripts/hx-backup.sh) are a real pg_dump + CTFd SQLite
    # snapshot + both uploads trees, bundled as .tar.gz. Legacy manual/scheduled
    # backups are a partial JSON snapshot (Users/AuditLog/BackupRecord only,
    # not a full database dump) bundled as .zip.
    if record.type == 'full':
        try:
            with tarfile.open(archive_path, 'r:gz') as tf:
                manifest_data = json.loads(tf.extractfile('manifest.json').read().decode('utf-8'))
        except Exception as e:
            return jsonify({'error': f'Corrupted backup archive: {e}'}), 400

        log_audit(
            'BACKUP_RESTORE_REQUIRES_CLI',
            target_type='BackupRecord',
            target_id=record.id,
            notes=f"Root admin requested restore of {record.filename}; full backups must be restored via scripts/hx-backup.sh (needs to stop/restart sibling containers, which this API process cannot safely do to itself)."
        )
        return jsonify({
            'error': 'cli_required',
            'message': (
                'This is a full backup (platform database + CTFd database + both uploads trees) '
                'and can be restored, but not from inside this API request: restoring stops and '
                'restarts the web, CTFd, and worker containers, which this running process cannot '
                'safely do to itself. Run the following on the host instead:\n\n'
                f'  ./scripts/hx-backup.sh restore {record.filename}'
            ),
            'manifest': manifest_data
        }), 501

    try:
        with zipfile.ZipFile(archive_path, 'r') as zf:
            manifest_data = json.loads(zf.read('manifest.json').decode('utf-8'))
    except Exception as e:
        return jsonify({'error': f'Corrupted backup archive: {e}'}), 400

    log_audit(
        'BACKUP_RESTORE_ATTEMPTED_NOT_IMPLEMENTED',
        target_type='BackupRecord',
        target_id=record.id,
        notes=f"Root admin requested restore of {record.filename}; this is a legacy partial-snapshot backup with no automated restore path."
    )

    # This legacy format only ever snapshotted Users/AuditLog/BackupRecord as a JSON
    # manifest, not a full database dump, so an automated restore here would silently
    # leave every other table (courses, competitions, chat, etc.) out of sync with the
    # "restored" users - worse than doing nothing during a real incident. There is no
    # manual procedure that fixes this either, since the data to restore the rest of
    # the schema from was simply never captured - take a new full backup going forward.
    return jsonify({
        'error': 'not_implemented',
        'message': (
            'Automated restore is not implemented for this legacy backup. It only contains '
            'a partial JSON snapshot (Users/AuditLog/BackupRecord), not a full database dump, '
            'so restoring it would leave other tables inconsistent - and the rest of the schema '
            'was never captured, so there is no way to complete it after the fact. Use '
            '"./scripts/hx-backup.sh backup" going forward for a fully restorable backup.'
        ),
        'manifest': manifest_data
    }), 501
