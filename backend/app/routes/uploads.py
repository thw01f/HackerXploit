from flask import Blueprint, request, jsonify
from app.services.upload_service import UploadPipeline, GENERIC_SECURITY_ERROR
from app.utils.decorators import require_auth, log_audit

uploads_bp = Blueprint('uploads', __name__, url_prefix='/api/uploads')

@uploads_bp.route('', methods=['POST'])
@require_auth
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': GENERIC_SECURITY_ERROR}), 400

    file_item = request.files['file']
    feature = request.form.get('feature', 'avatars')

    allowed_features = {'avatars', 'courses', 'course_attachments', 'competitions', 'certificates', 'opportunities', 'resumes'}
    if feature not in allowed_features:
        return jsonify({'error': GENERIC_SECURITY_ERROR}), 400

    try:
        result = UploadPipeline.process_and_save(file_item, feature=feature)
        log_audit('FILE_UPLOAD', target_type='File', details={'url': result['url'], 'feature': feature})
        return jsonify(result), 201
    except ValueError:
        return jsonify({'error': GENERIC_SECURITY_ERROR}), 400
    except Exception:
        return jsonify({'error': GENERIC_SECURITY_ERROR}), 400
