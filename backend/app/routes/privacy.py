import os
import json
import zipfile
from io import BytesIO
from datetime import datetime
from flask import Blueprint, request, jsonify, g, send_file, current_app
from app.models import (
    db, User, PublicProfileSetting, Certificate, Enrollment, ActivitySession,
    CompetitionParticipation, AuditLog
)
from app.utils.decorators import require_auth, log_audit

privacy_bp = Blueprint('privacy', __name__, url_prefix='/api/profile')

@privacy_bp.route('/privacy', methods=['GET'])
@require_auth
def get_privacy_settings():
    user = g.current_user
    settings = PublicProfileSetting.query.get(user.id)
    if not settings:
        settings = PublicProfileSetting(user_id=user.id, is_public=False, show_activity_hours=True, show_certificates=True)
        db.session.add(settings)
        db.session.commit()
    return jsonify(settings.to_dict()), 200

@privacy_bp.route('/privacy', methods=['POST'])
@require_auth
def update_privacy_settings():
    user = g.current_user
    data = request.get_json(silent=True) or {}

    settings = PublicProfileSetting.query.get(user.id)
    if not settings:
        settings = PublicProfileSetting(user_id=user.id)
        db.session.add(settings)

    if 'is_public' in data:
        settings.is_public = bool(data['is_public'])
    if 'show_activity_hours' in data:
        settings.show_activity_hours = bool(data['show_activity_hours'])
    if 'show_certificates' in data:
        settings.show_certificates = bool(data['show_certificates'])

    db.session.commit()
    log_audit('PRIVACY_SETTINGS_UPDATED', target_type='User', target_id=user.id, notes=f"is_public: {settings.is_public}")
    return jsonify(settings.to_dict()), 200

@privacy_bp.route('/request-deletion', methods=['POST'])
@require_auth
def request_account_deletion():
    user = g.current_user
    data = request.get_json(silent=True) or {}
    reason = data.get('reason', 'User initiated account deletion request')

    log_audit('ACCOUNT_DELETION_REQUESTED', target_type='User', target_id=user.id, notes=f"Reason: {reason}")
    return jsonify({
        'message': 'Account deletion request queued successfully. An administrator will review your request shortly.',
        'status': 'pending_review'
    }), 200

@privacy_bp.route('/export-my-data', methods=['GET'])
@require_auth
def export_user_data():
    user = g.current_user

    # Prepare JSON summary
    enrollments = Enrollment.query.filter_by(user_id=user.id).all()
    certificates = Certificate.query.filter_by(user_id=user.id).all()
    sessions = ActivitySession.query.filter_by(user_id=user.id).all()
    participations = CompetitionParticipation.query.filter_by(user_id=user.id).all()

    profile_data = {
        'account': user.to_dict(),
        'enrollments': [e.to_dict() for e in enrollments],
        'certificates': [c.to_dict() for c in certificates],
        'activity_sessions': [s.to_dict() for s in sessions],
        'competition_participations': [p.to_dict() for p in participations],
        'exported_at': datetime.utcnow().isoformat()
    }

    # Create Zip Archive in memory
    memory_file = BytesIO()
    base_upload = current_app.config.get('UPLOAD_FOLDER', '/var/uploads') if current_app else '/var/uploads'

    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Write JSON data
        zf.writestr('profile_summary.json', json.dumps(profile_data, indent=2))

        # Attach PDF certificates if they exist on disk
        for cert in certificates:
            if cert.file_path:
                rel_path = cert.file_path.lstrip('/')
                full_path = os.path.join(base_upload, rel_path.replace('uploads/', ''))
                if os.path.exists(full_path):
                    zf.write(full_path, arcname=f"certificates/{os.path.basename(full_path)}")

    memory_file.seek(0)
    log_audit('USER_DATA_EXPORTED', target_type='User', target_id=user.id)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"hackerxploit_data_export_{user.username}.zip"
    )
