import os
import io
import zipfile
import pytest
from PIL import Image
from werkzeug.datastructures import FileStorage

from app.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'

from app import create_app
from app.services.upload_service import UploadPipeline, GENERIC_SECURITY_ERROR

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        yield app

def test_renamed_extension_content_sniffing_rejection(app):
    """
    Test that a shell/python script disguised with a .png extension is detected
    by real-content MIME sniffing and rejected with a generic security error.
    """
    script_content = b"#!/bin/bash\necho 'Attempting malicious code execution'\nexit 0"
    file_item = FileStorage(
        stream=io.BytesIO(script_content),
        filename="malicious_payload.png",
        content_type="image/png"  # Spoofed browser header
    )

    # 1. Direct MIME detection test
    detected_mime = UploadPipeline.detect_mime(file_item)
    assert detected_mime != "image/png"
    assert detected_mime in ("text/plain", "text/x-shellscript", "application/octet-stream")

    # 2. Pipeline processing test - should raise generic security error
    with pytest.raises(ValueError) as excinfo:
        UploadPipeline.process_and_save(file_item, feature="avatars")
    
    assert str(excinfo.value) == GENERIC_SECURITY_ERROR

def test_image_resizing_and_thumbnail_generation(app, tmp_path):
    """
    Test uploading a high-resolution 2500x2500 image.
    Verifies that:
    1. Saved main image is resized to <= 1600px longest edge.
    2. Thumbnail image is generated alongside and is <= 300px longest edge.
    """
    app.config['UPLOAD_FOLDER'] = str(tmp_path / 'uploads')

    # Create 2500x2500 test image in memory
    img = Image.new('RGB', (2500, 2500), color='cyan')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()

    file_item = FileStorage(
        stream=io.BytesIO(img_bytes),
        filename="large_photo.png",
        content_type="image/png"
    )

    res = UploadPipeline.process_and_save(file_item, feature="avatars")

    assert res['url'].startswith("/uploads/avatars/")
    assert res['thumb_url'].startswith("/uploads/avatars/thumbs/")

    # Read back saved files to verify dimensions
    main_relative_path = res['url'].replace('/uploads/avatars/', '')
    main_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'avatars', main_relative_path)
    if not os.path.exists(main_file_path):
        main_file_path = os.path.join('/tmp/uploads', 'avatars', main_relative_path)

    saved_main_img = Image.open(main_file_path)
    w, h = saved_main_img.size
    assert max(w, h) <= 1600

    thumb_relative_path = res['thumb_url'].replace('/uploads/avatars/thumbs/', '')
    thumb_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'avatars', 'thumbs', thumb_relative_path)
    if not os.path.exists(thumb_file_path):
        thumb_file_path = os.path.join('/tmp/uploads', 'avatars', 'thumbs', thumb_relative_path)

    saved_thumb_img = Image.open(thumb_file_path)
    tw, th = saved_thumb_img.size
    assert max(tw, th) <= 300

def test_feature_scoped_allowlists(app):
    """
    Test feature allowlists:
    - ZIP uploaded to course_attachments -> accepted
    - ZIP uploaded to avatars -> rejected with generic security error
    """
    # Create valid ZIP stream
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.writestr('lab_instructions.txt', 'Lab 1 material')
    zip_bytes = zip_buffer.getvalue()

    # 1. Test course_attachments -> allowed
    zip_file_1 = FileStorage(
        stream=io.BytesIO(zip_bytes),
        filename="lab_materials.zip",
        content_type="application/zip"
    )
    res = UploadPipeline.process_and_save(zip_file_1, feature="course_attachments")
    assert res['mime'] in ('application/zip', 'application/x-zip-compressed')

    # 2. Test avatars -> rejected
    zip_file_2 = FileStorage(
        stream=io.BytesIO(zip_bytes),
        filename="avatar.zip",
        content_type="application/zip"
    )
    with pytest.raises(ValueError) as excinfo:
        UploadPipeline.process_and_save(zip_file_2, feature="avatars")
    
    assert str(excinfo.value) == GENERIC_SECURITY_ERROR

def test_valid_pdf_upload(app):
    """
    Test uploading a valid PDF document.
    """
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    pdf_file = FileStorage(
        stream=io.BytesIO(pdf_bytes),
        filename="document.pdf",
        content_type="application/pdf"
    )
    res = UploadPipeline.process_and_save(pdf_file, feature="certificates")
    assert res['mime'] == "application/pdf"
    assert res['thumb_url'] is None
