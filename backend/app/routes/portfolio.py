import os
from datetime import datetime
from flask import Blueprint, request, jsonify, g, send_file, current_app
from app.models import (
    db, User, Course, Enrollment, Certificate, CompetitionParticipation,
    Competition, ActivitySession, PublicProfileSetting
)
from app.utils.decorators import require_auth

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api')

@portfolio_bp.route('/portfolio/export-pdf', methods=['GET'])
@require_auth
def export_portfolio_pdf():
    user = g.current_user

    # Fetch user data
    completed_enrollments = Enrollment.query.filter_by(user_id=user.id, progress_percent=100.0).all()
    completed_courses = [Course.query.get(e.course_id) for e in completed_enrollments if Course.query.get(e.course_id)]

    certificates = Certificate.query.filter_by(user_id=user.id).all()
    participations = CompetitionParticipation.query.filter_by(user_id=user.id).all()

    activity_sessions = ActivitySession.query.filter_by(user_id=user.id).all()
    total_hours = round(sum(s.duration_seconds for s in activity_sessions) / 3600.0, 1)

    # Generate PDF file
    base_upload = current_app.config.get('UPLOAD_FOLDER', '/var/uploads') if current_app else '/var/uploads'
    output_dir = os.path.join(base_upload, 'portfolios')
    try:
        os.makedirs(output_dir, exist_ok=True)
    except (PermissionError, OSError):
        output_dir = "/tmp/uploads/portfolios"
        os.makedirs(output_dir, exist_ok=True)

    filename = f"portfolio_{user.username}_{int(datetime.utcnow().timestamp())}.pdf"
    file_path = os.path.join(output_dir, filename)

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors

        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter

        # Header
        c.setFillColor(colors.HexColor('#0F172A'))
        c.rect(0, height - 100, width, 100, fill=True, stroke=False)

        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(colors.HexColor('#00F0FF'))
        c.drawString(40, height - 50, user.username.upper())

        c.setFont("Helvetica", 12)
        c.setFillColor(colors.HexColor('#94A3B8'))
        c.drawString(40, height - 75, f"Cybersecurity Member | Role: {user.role.title()} | Member Since: {user.created_at.strftime('%b %Y')}")

        y = height - 140

        # Section 1: Summary Statistics
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor('#0F172A'))
        c.drawString(40, y, "EXECUTIVE SUMMARY")
        y -= 25

        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor('#334155'))
        c.drawString(50, y, f"• Total Learning & Lab Hours: {total_hours} Hours")
        y -= 18
        c.drawString(50, y, f"• Academy Curriculum Courses Completed: {len(completed_courses)}")
        y -= 18
        c.drawString(50, y, f"• Verified Platform Certificates: {len(certificates)}")
        y -= 18
        c.drawString(50, y, f"• Competition Participations & Placements: {len(participations)}")
        y -= 35

        # Section 2: Completed Courses
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor('#0F172A'))
        c.drawString(40, y, "ACADEMY CURRICULUM")
        y -= 25

        if completed_courses:
            for course in completed_courses[:5]:
                c.setFont("Helvetica-Bold", 12)
                c.setFillColor(colors.HexColor('#7000FF'))
                c.drawString(50, y, f"• {course.title}")
                y -= 16
                c.setFont("Helvetica", 10)
                c.setFillColor(colors.HexColor('#64748B'))
                desc_snippet = course.description[:100] + ('...' if len(course.description) > 100 else '')
                c.drawString(65, y, desc_snippet)
                y -= 22
        else:
            c.setFont("Helvetica-Oblique", 11)
            c.setFillColor(colors.HexColor('#64748B'))
            c.drawString(50, y, "No completed courses yet.")
            y -= 25

        y -= 15

        # Section 3: Competition Trophy Case
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor('#0F172A'))
        c.drawString(40, y, "COMPETITION TROPHY CASE")
        y -= 25

        if participations:
            for part in participations[:5]:
                comp = Competition.query.get(part.competition_id)
                comp_title = comp.title if comp else f"Competition #{part.competition_id}"
                c.setFont("Helvetica-Bold", 11)
                c.setFillColor(colors.HexColor('#0F172A'))
                c.drawString(50, y, f"• {comp_title}")
                c.setFont("Helvetica", 10)
                c.setFillColor(colors.HexColor('#00F0FF') if part.result == 'winner' else colors.HexColor('#64748B'))
                c.drawRightString(width - 40, y, f"Result: {part.result.upper()} ({part.placement_label or 'N/A'})")
                y -= 20
        else:
            c.setFont("Helvetica-Oblique", 11)
            c.setFillColor(colors.HexColor('#64748B'))
            c.drawString(50, y, "No competition participation records yet.")
            y -= 25

        # Footer
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor('#94A3B8'))
        c.drawString(40, 30, "Generated by HackerXploit Cybersecurity Platform")
        c.drawRightString(width - 40, 30, datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))

        c.save()
    except Exception:
        # Fallback text PDF if ReportLab fails
        fallback_content = f"HACKERXPLOIT PORTFOLIO: {user.username}\nHours: {total_hours}\nCourses: {len(completed_courses)}"
        with open(file_path, "wb") as f:
            f.write(fallback_content.encode('utf-8'))

    return send_file(file_path, as_attachment=True, download_name=f"HackerXploit_Portfolio_{user.username}.pdf")

@portfolio_bp.route('/profile/public/<username>', methods=['GET'])
def get_public_profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'Public profile not found'}), 404

    settings = PublicProfileSetting.query.get(user.id)
    if not settings or not settings.is_public:
        return jsonify({'error': 'This member profile is private'}), 404

    # Build public payload
    completed_enrollments = Enrollment.query.filter_by(user_id=user.id, progress_percent=100.0).all()
    courses = [Course.query.get(e.course_id).to_dict() for e in completed_enrollments if Course.query.get(e.course_id)]

    certificates = []
    if settings.show_certificates:
        cert_objs = Certificate.query.filter_by(user_id=user.id).all()
        certificates = [c.to_dict() for c in cert_objs]

    activity_hours = 0.0
    if settings.show_activity_hours:
        sessions = ActivitySession.query.filter_by(user_id=user.id).all()
        activity_hours = round(sum(s.duration_seconds for s in sessions) / 3600.0, 1)

    participations = CompetitionParticipation.query.filter_by(user_id=user.id).all()
    trophy_case = []
    for p in participations:
        comp = Competition.query.get(p.competition_id)
        if comp:
            trophy_case.append({
                'competition_title': comp.title,
                'category': comp.category,
                'result': p.result,
                'placement_label': p.placement_label,
                'submitted_at': p.submitted_at.isoformat() if p.submitted_at else None
            })

    return jsonify({
        'user': {
            'username': user.username,
            'role': user.role,
            'created_at': user.created_at.isoformat(),
            'avatar_url': getattr(user, 'avatar_url', None)
        },
        'stats': {
            'total_courses_completed': len(courses),
            'total_certificates': len(certificates) if settings.show_certificates else None,
            'total_activity_hours': activity_hours if settings.show_activity_hours else None,
            'leaderboard_score': getattr(user, 'leaderboard_score', 0.0)
        },
        'completed_courses': courses,
        'certificates': certificates,
        'trophy_case': trophy_case
    }), 200
