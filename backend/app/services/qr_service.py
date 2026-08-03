import io
import os
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image

_LOGO_PATH = os.path.join(os.path.dirname(__file__), '..', 'static', 'defaults', 'logo.png')


def generate_branded_qr_png(data: str) -> bytes:
    """
    Renders a QR code for `data` with the HackerXploit logo embedded in the
    center, matching the branded look used on the ID card. High (H, ~30%)
    error correction is used so the logo overlay doesn't break scannability -
    the standard technique for logo/branded QR codes.
    """
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color='black', back_color='white').convert('RGBA')

    try:
        logo = Image.open(_LOGO_PATH).convert('RGBA')
        qr_w, qr_h = qr_img.size
        logo_target = qr_w // 4
        logo.thumbnail((logo_target, logo_target), Image.Resampling.LANCZOS)

        # White rounded backing plate behind the logo so it stays legible
        # against whatever QR modules happen to sit underneath it.
        pad = 10
        plate_size = (logo.size[0] + pad * 2, logo.size[1] + pad * 2)
        plate = Image.new('RGBA', plate_size, (255, 255, 255, 255))
        plate_pos = ((qr_w - plate_size[0]) // 2, (qr_h - plate_size[1]) // 2)
        qr_img.paste(plate, plate_pos, plate)

        logo_pos = ((qr_w - logo.size[0]) // 2, (qr_h - logo.size[1]) // 2)
        qr_img.paste(logo, logo_pos, logo)
    except (FileNotFoundError, OSError):
        pass  # Fall back to a plain (unbranded) QR code if the logo asset is missing

    buf = io.BytesIO()
    qr_img.convert('RGB').save(buf, 'PNG')
    return buf.getvalue()
