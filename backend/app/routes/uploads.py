from flask import Blueprint, request, jsonify
from app.services.upload_service import UploadPipeline
from app.utils.decorators import require_auth, log_audit

uploads_bp = Blueprint('uploads', __name__, url_prefix='/api/uploads')

@uploads_bp.route('', methods=['POST'])
@require_auth
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400

    file_item = request.files['file']
    feature = request.form.get('feature', 'avatars')

    allowed_features = {'avatars', 'courses', 'competitions', 'certificates'}
    if feature not in allowed_features:
        return jsonify({'error': f"Invalid feature folder: '{feature}'"}), 400

    try:
        result = UploadPipeline.process_and_save(file_item, feature=feature)
        log_audit('FILE_UPLOAD', target_type='File', details={'url': result['url'], 'feature': feature})
        return jsonify(result), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': f"Upload failed: {str(e)}"}), 500
