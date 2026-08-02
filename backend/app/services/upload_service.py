import os
import uuid
import socket
import io
from PIL import Image
from flask import current_app

try:
    import magic
except ImportError:
    magic = None

# Feature-specific allowlists based on real MIME sniffing
STANDARD_ALLOWED_MIMES = {
    'image/jpeg',
    'image/png',
    'image/webp',
    'application/pdf'
}

COURSE_ATTACHMENT_MIMES = STANDARD_ALLOWED_MIMES | {
    'application/zip',
    'application/x-zip-compressed',
    'text/plain',
    'text/markdown',
    'text/x-markdown'
}

GENERIC_SECURITY_ERROR = "couldn't be verified as a valid file"

# Per-feature file size ceilings, enforced on top of the global Flask
# MAX_CONTENT_LENGTH - competition proof/photos are phone screenshots, not
# archives, so they get a tighter cap to keep disk usage predictable.
FEATURE_MAX_BYTES = {
    'competitions': 5 * 1024 * 1024,
}
FILE_TOO_LARGE_ERROR = "file exceeds the maximum allowed size (5MB)"

class UploadPipeline:
    @staticmethod
    def detect_mime(file_stream) -> str:
        """
        Reads initial bytes from file_stream to detect real MIME type using python-magic.
        Falls back to header byte signature checks if python-magic is unavailable.
        """
        file_stream.seek(0)
        header = file_stream.read(2048)
        file_stream.seek(0)

        if not header:
            return 'application/octet-stream'

        if magic:
            try:
                mime = magic.from_buffer(header, mime=True)
                if mime:
                    return mime
            except Exception:
                pass

        # Fallback signature checks for standard formats
        if header.startswith(b'\xff\xd8\xff'):
            return 'image/jpeg'
        elif header.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'image/png'
        elif header.startswith(b'%PDF'):
            return 'application/pdf'
        elif header.startswith(b'RIFF') and header[8:12] == b'WEBP':
            return 'image/webp'
        elif header.startswith(b'PK\x03\x04'):
            return 'application/zip'

        return 'application/octet-stream'

    @staticmethod
    def scan_clamav(file_bytes: bytes) -> tuple[bool, str]:
        """
        Scans file bytes with ClamAV daemon via INSTREAM protocol over socket.
        """
        host = current_app.config.get('CLAMAV_HOST', 'clamav') if current_app else 'clamav'
        port = int(current_app.config.get('CLAMAV_PORT', 3310)) if current_app else 3310

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3.0)
            s.connect((host, port))
            s.sendall(b'zINSTREAM\0')

            chunk_size = 2048
            for i in range(0, len(file_bytes), chunk_size):
                chunk = file_bytes[i:i + chunk_size]
                s.sendall(len(chunk).to_bytes(4, byteorder='big') + chunk)
            s.sendall((0).to_bytes(4, byteorder='big'))

            response = s.recv(1024).decode('utf-8', errors='ignore')
            s.close()
            if 'FOUND' in response:
                return False, f"Malware detected: {response.strip()}"
            return True, "Clean"
        except Exception:
            # Fail closed in production: an unreachable scanner must not silently
            # disable malware scanning. Dev/test environments (no ClamAV container
            # running) still pass through so local development isn't blocked.
            is_production = os.environ.get('FLASK_ENV', 'production') == 'production'
            if is_production:
                return False, "ClamAV daemon unreachable"
            return True, "ClamAV daemon offline (non-production, allowing)"

    @classmethod
    def process_and_save(cls, file_storage, feature: str = 'avatars') -> dict:
        """
        Processes and saves an uploaded file through security and image transformation pipeline.
        Raises ValueError(GENERIC_SECURITY_ERROR) for any security or processing failure.
        """
        file_bytes = file_storage.read()
        file_storage.seek(0)

        if not file_bytes:
            raise ValueError(GENERIC_SECURITY_ERROR)

        max_bytes = FEATURE_MAX_BYTES.get(feature)
        if max_bytes and len(file_bytes) > max_bytes:
            raise ValueError(FILE_TOO_LARGE_ERROR)

        # 1. Real MIME Sniffing via python-magic
        detected_mime = cls.detect_mime(file_storage)

        # Select appropriate allowlist based on feature context
        allowed_mimes = COURSE_ATTACHMENT_MIMES if feature in ('course_attachments', 'courses') else STANDARD_ALLOWED_MIMES

        if detected_mime not in allowed_mimes:
            raise ValueError(GENERIC_SECURITY_ERROR)

        # 2. ClamAV Virus Scan
        is_clean, _ = cls.scan_clamav(file_bytes)
        if not is_clean:
            raise ValueError(GENERIC_SECURITY_ERROR)

        # 3. Base directory setup
        upload_base = current_app.config.get('UPLOAD_FOLDER', '/var/uploads') if current_app else '/var/uploads'
        target_dir = os.path.join(upload_base, feature)
        try:
            os.makedirs(target_dir, exist_ok=True)
        except (PermissionError, OSError):
            target_dir = os.path.join('/tmp/uploads', feature)
            os.makedirs(target_dir, exist_ok=True)

        filename_uuid = uuid.uuid4().hex

        # 4. Image Resizing & Thumbnail Generation (Pillow)
        if detected_mime in ('image/jpeg', 'image/png', 'image/webp'):
            try:
                # Verify and open image
                img_io = io.BytesIO(file_bytes)
                img = Image.open(img_io)
                img.verify()

                # Re-open for transformation
                img_io.seek(0)
                img = Image.open(img_io)
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')

                # Resize to capped maximum dimension (1600px longest edge)
                img.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
                
                full_filename = f"{filename_uuid}.webp"
                full_path = os.path.join(target_dir, full_filename)
                img.save(full_path, 'WEBP', quality=85)

                # Generate small thumbnail variant (300px longest edge)
                thumb_dir = os.path.join(target_dir, 'thumbs')
                os.makedirs(thumb_dir, exist_ok=True)
                
                thumb_img = img.copy()
                thumb_img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                thumb_filename = f"thumb_{filename_uuid}.webp"
                thumb_path = os.path.join(thumb_dir, thumb_filename)
                thumb_img.save(thumb_path, 'WEBP', quality=80)

                return {
                    'url': f"/uploads/{feature}/{full_filename}",
                    'thumb_url': f"/uploads/{feature}/thumbs/{thumb_filename}",
                    'mime': 'image/webp',
                    'size': os.path.getsize(full_path)
                }
            except Exception:
                raise ValueError(GENERIC_SECURITY_ERROR)

        # 5. Non-image document storage (PDF, ZIP, MD)
        ext = 'pdf' if detected_mime == 'application/pdf' else ('zip' if 'zip' in detected_mime else 'txt')
        full_filename = f"{filename_uuid}.{ext}"
        full_path = os.path.join(target_dir, full_filename)

        with open(full_path, 'wb') as f:
            f.write(file_bytes)

        return {
            'url': f"/uploads/{feature}/{full_filename}",
            'thumb_url': None,
            'mime': detected_mime,
            'size': len(file_bytes)
        }

    @staticmethod
    def delete_uploaded_file(url: str):
        """
        Best-effort removal of a previously uploaded file (and its thumbnail, if
        any) from disk given its public /uploads/... URL. Used for space-saving
        cleanup (e.g. registration proof deleted once superseded by an event
        completion report) - failures are swallowed since a missing file on
        disk should never block the caller's own transaction.
        """
        if not url or not url.startswith('/uploads/'):
            return
        upload_base = current_app.config.get('UPLOAD_FOLDER', '/var/uploads') if current_app else '/var/uploads'
        relative_path = url[len('/uploads/'):]
        candidates = [os.path.join(upload_base, relative_path)]

        filename = os.path.basename(relative_path)
        dirname = os.path.dirname(relative_path)
        candidates.append(os.path.join(upload_base, dirname, 'thumbs', f'thumb_{filename}'))

        for path in candidates:
            try:
                if os.path.isfile(path):
                    os.remove(path)
            except OSError:
                pass
