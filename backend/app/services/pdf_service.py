import os
from datetime import datetime
from flask import current_app

def generate_completion_certificate(user_full_name: str, course_title: str, cert_id: str, output_dir: str = None) -> str:
    """
    Generates a PDF certificate file for a completed course or competition.
    Returns the relative web-accessible file path of the generated certificate.
    """
    if not output_dir:
        base_upload = current_app.config.get('UPLOAD_FOLDER', '/var/uploads') if current_app else '/var/uploads'
        output_dir = os.path.join(base_upload, 'certificates')

    try:
        os.makedirs(output_dir, exist_ok=True)
    except (PermissionError, OSError):
        output_dir = "/tmp/uploads/certificates"
        os.makedirs(output_dir, exist_ok=True)

    filename = f"certificate_{cert_id}.pdf"
    file_path = os.path.join(output_dir, filename)

    try:
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors

        c = canvas.Canvas(file_path, pagesize=landscape(letter))
        width, height = landscape(letter)

        # Outer Border
        c.setStrokeColor(colors.HexColor('#00F0FF'))
        c.setLineWidth(5)
        c.rect(20, 20, width - 40, height - 40)

        # Inner Decorative Border
        c.setStrokeColor(colors.HexColor('#7000FF'))
        c.setLineWidth(1.5)
        c.rect(30, 30, width - 60, height - 60)

        # Header Title
        c.setFont("Helvetica-Bold", 32)
        c.setFillColor(colors.HexColor('#0F172A'))
        c.drawCentredString(width / 2.0, height - 100, "HACKERXPLOIT PLATFORM")

        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(colors.HexColor('#00F0FF'))
        c.drawCentredString(width / 2.0, height - 140, "CERTIFICATE OF COMPLETION")

        # Recipient
        c.setFont("Helvetica", 14)
        c.setFillColor(colors.HexColor('#475569'))
        c.drawCentredString(width / 2.0, height - 200, "This is proudly presented to")

        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(colors.HexColor('#0F172A'))
        c.drawCentredString(width / 2.0, height - 250, user_full_name or "Cybersecurity Scholar")

        # Course details
        c.setFont("Helvetica", 14)
        c.setFillColor(colors.HexColor('#475569'))
        c.drawCentredString(width / 2.0, height - 300, "for successfully mastering and completing the curriculum of")

        c.setFont("Helvetica-Bold", 22)
        c.setFillColor(colors.HexColor('#7000FF'))
        c.drawCentredString(width / 2.0, height - 340, f"\"{course_title}\"")

        # Footer Date & Verification ID
        issued_str = datetime.utcnow().strftime("%B %d, %Y")
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.HexColor('#64748B'))
        c.drawString(60, 60, f"Issued Date: {issued_str}")
        c.drawRightString(width - 60, 60, f"Verification ID: {cert_id}")

        c.save()
    except ImportError:
        pdf_content = f"""%PDF-1.4
1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj
2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj
3 0 obj <</Type /Page /Parent 2 0 R /Resources <</Font <</F1 4 0 R>>>> /Contents 5 0 R>> endobj
4 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold>> endobj
5 0 obj <</Length 200>> stream
BT
/F1 24 Tf
100 500 TD
(HACKERXPLOIT CERTIFICATE OF COMPLETION) Tj
/F1 16 Tf
0 -40 TD
(Awarded to: {user_full_name}) Tj
0 -30 TD
(Course: {course_title}) Tj
0 -30 TD
(ID: {cert_id}) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000216 00000 n 
0000000293 00000 n 
trailer <</Size 6 /Root 1 0 R>>
startxref
548
%%EOF"""
        with open(file_path, "wb") as f:
            f.write(pdf_content.encode('utf-8'))

    return f"/uploads/certificates/{filename}"
