import csv
import io
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g, make_response
from app.models import db, Competition, CompetitionParticipation, User, Certificate, EventAttendance, IDCardToken
from app.utils.decorators import require_auth, require_role, log_audit
from app.services.pdf_service import generate_completion_certificate
from app.services.upload_service import UploadPipeline

from sqlalchemy import func

MAX_APPLICATION_SCREENSHOTS = 3
MAX_EVENT_PHOTOS = 5

competition_bp = Blueprint('competition', __name__, url_prefix='/api/competitions')

@competition_bp.route('', methods=['GET'])
@require_auth
def get_competitions():
    category = request.args.get('category', 'All')
    status_filter = request.args.get('status', 'all')
    priority_filter = request.args.get('priority', 'all')
    involvement_filter = request.args.get('involvement', 'all')

    query = Competition.query.filter_by(is_archived=False)

    if category and category != 'All':
        query = query.filter(Competition.category.ilike(category))

    if status_filter and status_filter != 'all':
        query = query.filter_by(status=status_filter)

    if priority_filter and priority_filter != 'all':
        query = query.filter_by(priority=priority_filter)

    competitions = query.all()

    # User involvement mapping for current user
    user_participations = {
        p.competition_id: p for p in CompetitionParticipation.query.filter_by(user_id=g.current_user.id).all()
    }

    results = []
    for c in competitions:
        p = user_participations.get(c.id)
        # Filter matching stays keyed off the base registration status so
        # 'applied'/'verified' filters keep working the same regardless of
        # whether the student has since filed a post-event completion report.
        base_status = p.application_status if p else 'not_applied'

        # Display label is richer: once a completion report is filed it takes
        # precedence, since it's the more advanced/current state of involvement.
        if p and p.completion_status == 'verified':
            user_involvement = 'completed'
        elif p and p.completion_status == 'pending_review':
            user_involvement = 'completion_pending'
        else:
            user_involvement = base_status

        if involvement_filter != 'all':
            if involvement_filter == 'applied' and base_status == 'not_applied':
                continue
            if involvement_filter == 'verified' and base_status != 'verified':
                continue
            if involvement_filter == 'not_applied' and base_status != 'not_applied':
                continue
            if involvement_filter == 'completion_pending' and user_involvement != 'completion_pending':
                continue
            if involvement_filter == 'completed' and user_involvement != 'completed':
                continue

        c_dict = c.to_dict()
        c_dict['user_involvement'] = user_involvement
        c_dict['user_participation'] = p.to_dict() if p else None
        results.append(c_dict)

    # Sort priority-first (high=0, medium=1, normal=2) then soonest deadline
    priority_map = {'high': 0, 'medium': 1, 'normal': 2}
    
    def sort_key(item):
        p_val = priority_map.get(item['priority'], 2)
        deadline = item['application_deadline'] or item['starts_at'] or '9999-12-31'
        return (p_val, deadline)

    results.sort(key=sort_key)

    return jsonify({'competitions': results}), 200

def get_kolkata_now():
    """Returns current time in Asia/Kolkata (IST: UTC + 5:30) as naive datetime."""
    return datetime.utcnow() + timedelta(hours=5, minutes=30)


def parse_naive_datetime(iso_str):
    """
    Parses a client-supplied ISO datetime string, stripping any timezone offset.
    All datetimes in this system are naive wall-clock values (see get_kolkata_now) -
    a client sending an offset/'Z'-suffixed string must not crash the comparison
    below with a naive-vs-aware TypeError.
    """
    dt = datetime.fromisoformat(iso_str)
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt


@competition_bp.route('', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def announce_competition():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    description = data.get('description', '')
    starts_at_str = data.get('starts_at') or data.get('start_date')
    ends_at_str = data.get('ends_at') or data.get('end_date')

    if not title or not starts_at_str or not ends_at_str:
        return jsonify({'error': 'Title, starts_at, and ends_at dates are required'}), 400

    starts_at = parse_naive_datetime(starts_at_str)
    ends_at = parse_naive_datetime(ends_at_str)
    deadline = parse_naive_datetime(data['application_deadline']) if data.get('application_deadline') else None

    if ends_at <= starts_at:
        return jsonify({'error': 'Ends At must be after Starts At'}), 400
    if deadline and deadline > starts_at:
        return jsonify({'error': 'Application Deadline must be on or before Starts At'}), 400

    # Compute status based on Kolkata (IST) current time
    now_ist = get_kolkata_now()
    if now_ist < starts_at:
        status = 'upcoming'
    elif starts_at <= now_ist <= ends_at:
        status = 'ongoing'
    else:
        status = 'ended'

    comp = Competition(
        title=title,
        description=description,
        poster_image=data.get('poster_image'),
        external_link=data.get('external_link'),
        starts_at=starts_at,
        ends_at=ends_at,
        application_deadline=deadline,
        category=data.get('category', 'ctf'),
        priority=data.get('priority', 'normal'),
        posted_by_id=g.current_user.id,
        status=status
    )
    db.session.add(comp)
    db.session.commit()

    log_audit('COMPETITION_ANNOUNCE', target_type='Competition', target_id=comp.id, details={'title': title})
    return jsonify(comp.to_dict()), 201

@competition_bp.route('/<int:comp_id>', methods=['PUT'])
@require_role('teacher', 'admin', 'root_admin')
def update_competition(comp_id):
    comp = Competition.query.get_or_404(comp_id)
    data = request.get_json() or {}

    if 'title' in data and data['title'].strip():
        comp.title = data['title'].strip()
    if 'description' in data:
        comp.description = data['description']
    if 'category' in data:
        comp.category = data['category']
    if 'priority' in data:
        comp.priority = data['priority']
    if 'poster_image' in data:
        comp.poster_image = data['poster_image']
    if 'external_link' in data:
        comp.external_link = data['external_link']
    new_starts_at = parse_naive_datetime(data['starts_at']) if data.get('starts_at') else comp.starts_at
    new_ends_at = parse_naive_datetime(data['ends_at']) if data.get('ends_at') else comp.ends_at
    if 'application_deadline' in data:
        new_deadline = parse_naive_datetime(data['application_deadline']) if data['application_deadline'] else None
    else:
        new_deadline = comp.application_deadline

    if new_ends_at <= new_starts_at:
        return jsonify({'error': 'Ends At must be after Starts At'}), 400
    if new_deadline and new_deadline > new_starts_at:
        return jsonify({'error': 'Application Deadline must be on or before Starts At'}), 400

    comp.starts_at = new_starts_at
    comp.ends_at = new_ends_at
    comp.application_deadline = new_deadline

    # Re-evaluate status based on Kolkata time
    now_ist = get_kolkata_now()
    if now_ist < comp.starts_at:
        comp.status = 'upcoming'
    elif comp.starts_at <= now_ist <= comp.ends_at:
        comp.status = 'ongoing'
    else:
        comp.status = 'ended'

    db.session.commit()
    log_audit('COMPETITION_UPDATE', target_type='Competition', target_id=comp.id, details={'title': comp.title})
    return jsonify(comp.to_dict()), 200

@competition_bp.route('/<int:comp_id>', methods=['DELETE'])
@require_role('teacher', 'admin', 'root_admin')
def delete_competition(comp_id):
    comp = Competition.query.get_or_404(comp_id)
    title = comp.title
    
    # Clean up associated participations and attendance records
    CompetitionParticipation.query.filter_by(competition_id=comp_id).delete()
    EventAttendance.query.filter_by(competition_id=comp_id).delete()

    db.session.delete(comp)
    db.session.commit()

    log_audit('COMPETITION_DELETE', target_type='Competition', target_id=comp_id, details={'title': title})
    return jsonify({'message': f'Event "{title}" deleted successfully'}), 200

@competition_bp.route('/<int:comp_id>/apply', methods=['POST'])
@require_auth
def apply_competition(comp_id):
    comp = Competition.query.get_or_404(comp_id)
    data = request.get_json() or {}
    screenshots = data.get('application_screenshots')
    if screenshots is None:
        # Back-compat with any older single-URL callers
        single = data.get('application_screenshot')
        screenshots = [single] if single else []

    if not isinstance(screenshots, list) or not screenshots:
        return jsonify({'error': 'Application registration screenshot proof is required'}), 400
    if len(screenshots) > MAX_APPLICATION_SCREENSHOTS:
        return jsonify({'error': f'Maximum {MAX_APPLICATION_SCREENSHOTS} registration screenshots allowed'}), 400

    # Club events don't require any registration proof - reject stray applications against them.
    if (comp.category or '').lower() == 'club':
        return jsonify({'error': 'Club events do not require registration proof. Use the event feedback form instead.'}), 400

    existing = CompetitionParticipation.query.filter_by(competition_id=comp_id, user_id=g.current_user.id).first()
    if existing:
        existing.application_screenshots = screenshots
        existing.application_status = 'pending_verification'
        existing.applied_at = datetime.utcnow()
        db.session.commit()
        return jsonify(existing.to_dict()), 200

    part = CompetitionParticipation(
        competition_id=comp_id,
        user_id=g.current_user.id,
        application_screenshots=screenshots,
        application_status='pending_verification',
        applied_at=datetime.utcnow()
    )
    db.session.add(part)
    db.session.commit()

    log_audit('COMPETITION_APPLY', target_type='CompetitionParticipation', target_id=part.id)
    return jsonify(part.to_dict()), 201


@competition_bp.route('/<int:comp_id>/complete', methods=['POST'])
@require_auth
def submit_completion_report(comp_id):
    """
    Student self-service post-event report, filed once the competition has
    ended and their registration was staff-verified. Feeds into the staff
    Wrap-up queue as pending_review; staff finalization there (file_wrapup)
    is what promotes it to 'verified'. On successful submission, the now
    superseded registration-proof screenshots are deleted from disk.
    """
    comp = Competition.query.get_or_404(comp_id)
    part = CompetitionParticipation.query.filter_by(competition_id=comp_id, user_id=g.current_user.id).first()

    if not part:
        return jsonify({'error': 'You have not applied to this competition'}), 404
    if part.application_status != 'verified':
        return jsonify({'error': 'Your registration must be staff-verified before filing an event completion report'}), 403
    if comp.status != 'ended':
        return jsonify({'error': 'This competition has not ended yet'}), 400

    data = request.get_json() or {}
    event_photos = data.get('event_photos') or []
    if not isinstance(event_photos, list):
        return jsonify({'error': 'event_photos must be a list'}), 400
    if len(event_photos) > MAX_EVENT_PHOTOS:
        return jsonify({'error': f'Maximum {MAX_EVENT_PHOTOS} event photos allowed'}), 400

    self_reported_result = data.get('self_reported_result', 'participated')
    if self_reported_result not in ('participated', 'winner', 'runner_up', 'not_selected'):
        self_reported_result = 'participated'

    part.event_photos = event_photos
    part.summary_notes = (data.get('summary_notes') or '').strip() or None
    part.github_link = (data.get('github_link') or '').strip() or None
    part.prize_money = (data.get('prize_money') or '').strip() or None
    part.user_certificate_file = data.get('user_certificate_file') or None
    part.self_reported_result = self_reported_result
    part.completion_status = 'pending_review'
    part.completion_submitted_at = datetime.utcnow()

    # Space-saving cleanup: the registration proof is now superseded by the
    # completion report's own evidence (photos/certificate/result).
    for old_url in (part.application_screenshots or []):
        UploadPipeline.delete_uploaded_file(old_url)
    part.application_screenshots = []

    db.session.commit()

    log_audit('COMPETITION_COMPLETION_SUBMIT', target_type='CompetitionParticipation', target_id=part.id)
    return jsonify(part.to_dict()), 200

@competition_bp.route('/<int:comp_id>/applications', methods=['GET'])
@require_role('teacher', 'admin', 'root_admin')
def get_applications_queue(comp_id):
    comp = Competition.query.get_or_404(comp_id)
    participations = CompetitionParticipation.query.filter_by(competition_id=comp_id).all()

    queue = []
    for p in participations:
        u = User.query.get(p.user_id)
        p_dict = p.to_dict()
        p_dict['applicant_username'] = u.username if u else 'Unknown'
        p_dict['applicant_email'] = u.email if u else None
        p_dict['applicant_full_name'] = u.full_name if u else u.username
        queue.append(p_dict)

    return jsonify({'competition': comp.to_dict(), 'applications': queue}), 200

@competition_bp.route('/<int:comp_id>/applications/export', methods=['GET'])
@require_role('teacher', 'admin', 'root_admin')
def export_applications(comp_id):
    comp = Competition.query.get_or_404(comp_id)
    participations = CompetitionParticipation.query.filter_by(competition_id=comp_id).order_by(CompetitionParticipation.applied_at.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Badge ID', 'Student ID', 'Full Name', 'Username', 'Email', 'Academic Year', 'Department',
        'Application Status', 'Applied At', 'Verified By', 'Verified At',
        'Result', 'Placement Label', 'Completion Status', 'GitHub Link', 'Prize Money'
    ])

    for p in participations:
        u = User.query.get(p.user_id)
        verifier = User.query.get(p.verified_by_id) if p.verified_by_id else None
        writer.writerow([
            u.get_badge_id() if u else 'N/A',
            u.student_id if u and u.student_id else 'N/A',
            u.full_name if u else (u.username if u else 'Unknown'),
            u.username if u else 'Unknown',
            u.email if u else 'N/A',
            u.academic_year if u else 'N/A',
            u.department if u else 'N/A',
            p.application_status.upper(),
            p.applied_at.isoformat() if p.applied_at else '',
            verifier.full_name or verifier.username if verifier else '',
            p.verified_at.isoformat() if p.verified_at else '',
            p.result or '',
            p.placement_label or '',
            p.completion_status.upper(),
            p.github_link or '',
            p.prize_money or ''
        ])

    csv_data = output.getvalue()
    response = make_response(csv_data)
    filename = f"competition_applications_{comp_id}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    return response


@competition_bp.route('/<int:comp_id>/applications/<int:app_id>/verify', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def verify_application(comp_id, app_id):
    part = CompetitionParticipation.query.get_or_404(app_id)
    data = request.get_json() or {}
    status = data.get('status', 'verified')  # verified or rejected

    part.application_status = status
    part.verified_by_id = g.current_user.id
    part.verified_at = datetime.utcnow()
    db.session.commit()

    log_audit('COMPETITION_VERIFY_APP', target_type='CompetitionParticipation', target_id=app_id, details={'status': status})
    return jsonify(part.to_dict()), 200

@competition_bp.route('/<int:comp_id>/wrapup', methods=['POST'])
@require_role('teacher', 'admin', 'root_admin')
def file_wrapup(comp_id):
    comp = Competition.query.get_or_404(comp_id)
    data = request.get_json() or {}

    # Participations wrap-up update list: [{ 'participation_id': 1, 'result': 'winner', 'placement_label': '1st Place', ... }]
    updates = data.get('participants', [])
    summary_notes = data.get('summary_notes', '')
    event_photos = data.get('event_photos', [])

    comp.status = 'ended'
    
    for item in updates:
        part_id = item.get('participation_id')
        part = CompetitionParticipation.query.get(part_id)
        if not part:
            continue

        result_type = item.get('result') or part.self_reported_result or 'participated'
        part.result = result_type
        part.placement_label = item.get('placement_label')
        # Only overwrite the student's own submitted photos/notes if staff explicitly
        # supplied a replacement - an empty global default must never wipe them out.
        if item.get('summary_notes'):
            part.summary_notes = item.get('summary_notes')
        elif not part.summary_notes and summary_notes:
            part.summary_notes = summary_notes
        if item.get('event_photos'):
            part.event_photos = item.get('event_photos')
        elif not part.event_photos and event_photos:
            part.event_photos = event_photos
        part.submitted_by_id = g.current_user.id
        part.submitted_at = datetime.utcnow()

        # Finalizing wrap-up is the staff sign-off step for any completion report the student filed.
        if part.completion_status == 'pending_review':
            part.completion_status = 'verified'

        # If winner or runner_up, generate official platform certificate
        if result_type in ('winner', 'runner_up'):
            u = User.query.get(part.user_id)
            user_name = u.full_name or u.username if u else "Competitor"
            cert_id = f"COMP-{comp.id}-{part.user_id}"
            title_text = f"{comp.title} ({item.get('placement_label', result_type.capitalize())})"
            
            pdf_path = generate_completion_certificate(user_name, title_text, cert_id)
            part.certificate_file = pdf_path

            # Create Certificate table row
            cert = Certificate(
                user_id=part.user_id,
                type='competition',
                source_id=comp.id,
                file_path=pdf_path
            )
            db.session.add(cert)

    db.session.commit()

    log_audit('COMPETITION_WRAPUP', target_type='Competition', target_id=comp.id)
    return jsonify(comp.to_dict()), 200

# ==================== CLUB EVENT ATTENDANCE & SCANNER ROUTES ====================

@competition_bp.route('/club-events/active', methods=['GET'])
@require_role('teacher', 'admin')
def get_active_club_events():
    now_ist = get_kolkata_now()

    # Fetch active non-archived Club category events (case-insensitive)
    events = Competition.query.filter(
        Competition.is_archived == False,
        func.lower(Competition.category).contains('club')
    ).order_by(Competition.starts_at.desc()).all()

    # Smart Fallback: If no explicit 'club' category event is present, return all non-archived competitions
    if not events:
        events = Competition.query.filter(
            Competition.is_archived == False
        ).order_by(Competition.starts_at.desc()).all()

    results = []
    for comp in events:
        scan_open = comp.starts_at - timedelta(minutes=30)
        scan_close = comp.ends_at + timedelta(minutes=30) if comp.ends_at else comp.starts_at + timedelta(hours=4)

        # Scheduled window check against Kolkata IST time - the scanner is
        # only ever active in this window, with no role-based bypass. Access
        # to the scanner at all is separately restricted to teachers/admins
        # via the @require_role decorator on this route.
        in_scheduled_window = (scan_open <= now_ist <= scan_close)
        is_scan_allowed = in_scheduled_window

        comp_dict = comp.to_dict()
        comp_dict['scan_open_iso'] = scan_open.isoformat()
        comp_dict['scan_close_iso'] = scan_close.isoformat()
        comp_dict['in_scheduled_window'] = in_scheduled_window
        comp_dict['is_scan_allowed'] = is_scan_allowed

        # Count total scanned attendees so far
        attendee_count = EventAttendance.query.filter_by(competition_id=comp.id).count()
        comp_dict['attendee_count'] = attendee_count

        results.append(comp_dict)

    return jsonify({'club_events': results}), 200


def _resolve_scanned_user(token_input):
    """Resolves a scanned/typed QR payload (a full verify URL, a raw token,
    a badge ID, a username, or a numeric user id) to a User. Shared by the
    lookup (preview) and scan (record) steps so both use identical matching."""
    target_user = None
    raw_token = token_input

    # Handle full verification URLs (e.g. https://.../verify/TOKEN or http://.../verify?token=XYZ)
    if '/verify/' in token_input:
        token_input = token_input.split('/verify/')[-1].split('?')[0].split('/')[0].strip()
    elif 'token=' in token_input:
        token_input = token_input.split('token=')[-1].split('&')[0].strip()

    # 1. Search by token (try extracted token, then raw token)
    tok_obj = IDCardToken.query.filter_by(token=token_input).first() or IDCardToken.query.filter_by(token=raw_token).first()
    if tok_obj:
        target_user = User.query.get(tok_obj.user_id)

    # 2. Search by Badge ID (User has no member_id column - that's a display
    # value computed from badge_id, so look up by the real column)
    if not target_user:
        target_user = User.query.filter_by(badge_id=token_input).first()

    # 3. Search by username
    if not target_user:
        target_user = User.query.filter_by(username=token_input).first()

    # 4. Search by numeric user id
    if not target_user and token_input.isdigit():
        target_user = User.query.get(int(token_input))

    return target_user


def _scan_window_open(comp):
    now_ist = get_kolkata_now()
    scan_open = comp.starts_at - timedelta(minutes=30)
    scan_close = comp.ends_at + timedelta(minutes=30) if comp.ends_at else comp.starts_at + timedelta(hours=4)
    return scan_open <= now_ist <= scan_close


@competition_bp.route('/<int:comp_id>/attendance/lookup', methods=['POST'])
@require_role('teacher', 'admin')
def lookup_event_attendance(comp_id):
    """Read-only preview step: resolves a scanned/typed code to a member and
    returns their details (plus whether they're already marked present) so
    the scanner can show who it found before anything is recorded."""
    comp = Competition.query.get_or_404(comp_id)
    data = request.get_json() or {}
    token_input = (data.get('token') or data.get('member_id') or data.get('code') or '').strip()

    if not token_input:
        return jsonify({'error': 'QR Code, Token, or Member ID is required'}), 400

    if not _scan_window_open(comp):
        return jsonify({
            'error': f'Scanner inactive! Official attendance window for "{comp.title}" is closed.'
        }), 400

    target_user = _resolve_scanned_user(token_input)
    if not target_user:
        return jsonify({'error': 'Invalid QR badge code or member not found'}), 404

    existing = EventAttendance.query.filter_by(competition_id=comp_id, user_id=target_user.id).first()

    return jsonify({
        'member': {
            'id': target_user.id,
            'username': target_user.username,
            'full_name': target_user.full_name or target_user.username,
            'avatar_url': target_user.avatar_url,
            'badge_id': target_user.get_badge_id(),
            'role': target_user.role,
            'department': target_user.department,
            'academic_year': target_user.academic_year
        },
        'already_scanned': existing is not None,
        'attendance': existing.to_dict() if existing else None
    }), 200


@competition_bp.route('/<int:comp_id>/attendance/scan', methods=['POST'])
@require_role('teacher', 'admin')
def scan_event_attendance(comp_id):
    comp = Competition.query.get_or_404(comp_id)
    data = request.get_json() or {}

    token_input = (data.get('token') or data.get('member_id') or data.get('code') or '').strip()
    remark = (data.get('remark') or '').strip()

    if not token_input:
        return jsonify({'error': 'QR Code, Token, or Member ID is required'}), 400

    # 30-minute pre-start and post-end window check with Kolkata (IST) time -
    # applies unconditionally, with no role-based bypass. Who may reach this
    # route at all is separately restricted to teachers/admins via
    # @require_role above.
    if not _scan_window_open(comp):
        return jsonify({
            'error': f'Scanner inactive! Official attendance window for "{comp.title}" is closed.'
        }), 400

    target_user = _resolve_scanned_user(token_input)
    if not target_user:
        return jsonify({'error': 'Invalid QR badge code or member not found'}), 404

    # Record or update attendance
    attendance = EventAttendance.query.filter_by(competition_id=comp_id, user_id=target_user.id).first()
    if attendance:
        attendance.scanned_by_id = g.current_user.id
        attendance.scanned_at = datetime.utcnow()
        if remark:
            attendance.remark = remark
        attendance.status = 'approved'
    else:
        attendance = EventAttendance(
            competition_id=comp_id,
            user_id=target_user.id,
            scanned_by_id=g.current_user.id,
            scanned_at=datetime.utcnow(),
            status='approved',
            remark=remark
        )
        db.session.add(attendance)

    db.session.commit()

    log_audit('EVENT_ATTENDANCE_SCAN', target_type='EventAttendance', target_id=attendance.id, details={
        'competition_id': comp_id,
        'user_id': target_user.id,
        'remark': remark
    })

    return jsonify({
        'message': f'Attendance approved for {target_user.full_name or target_user.username}!',
        'attendance': attendance.to_dict()
    }), 200


@competition_bp.route('/<int:comp_id>/attendance', methods=['GET'])
@require_auth
def get_event_attendance(comp_id):
    comp = Competition.query.get_or_404(comp_id)
    records = EventAttendance.query.filter_by(competition_id=comp_id).order_by(EventAttendance.scanned_at.desc()).all()
    return jsonify({
        'competition': comp.to_dict(),
        'attendees': [r.to_dict() for r in records]
    }), 200


@competition_bp.route('/<int:comp_id>/attendance/export', methods=['GET'])
@require_role('teacher', 'admin', 'root_admin')
def export_event_attendance(comp_id):
    comp = Competition.query.get_or_404(comp_id)
    records = EventAttendance.query.filter_by(competition_id=comp_id).order_by(EventAttendance.scanned_at.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # CSV Header
    writer.writerow([
        'Badge ID', 'Full Name', 'Username', 'Email',
        'Academic Year', 'Department', 'Status', 'Scanned At', 'Approved By', 'Remark'
    ])

    for r in records:
        u = User.query.get(r.user_id)
        scanned_by = User.query.get(r.scanned_by_id) if r.scanned_by_id else None
        writer.writerow([
            u.get_badge_id() if u else 'N/A',
            u.full_name if u else (u.username if u else 'Unknown'),
            u.username if u else 'Unknown',
            u.email if u else 'N/A',
            u.academic_year if u else 'N/A',
            u.department if u else 'N/A',
            r.status.upper(),
            r.scanned_at.isoformat() if r.scanned_at else '',
            scanned_by.full_name or scanned_by.username if scanned_by else 'Self/System',
            r.remark or ''
        ])

    csv_data = output.getvalue()
    response = make_response(csv_data)
    filename = f"club_event_attendance_{comp_id}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    return response


# ==================== CLUB EVENT FEEDBACK ENDPOINTS ====================

@competition_bp.route('/<int:comp_id>/feedback', methods=['GET'])
@require_auth
def get_event_feedback(comp_id):
    from app.models import ClubEventFeedback
    comp = Competition.query.get_or_404(comp_id)
    feedbacks = ClubEventFeedback.query.filter_by(competition_id=comp_id).order_by(ClubEventFeedback.created_at.desc()).all()
    
    user_fb = ClubEventFeedback.query.filter_by(competition_id=comp_id, user_id=g.current_user.id).first()
    
    total_ratings = len(feedbacks)
    avg_rating = round(sum(f.rating for f in feedbacks) / total_ratings, 1) if total_ratings > 0 else 0.0

    return jsonify({
        'feedbacks': [f.to_dict() for f in feedbacks],
        'user_feedback': user_fb.to_dict() if user_fb else None,
        'total_ratings': total_ratings,
        'avg_rating': avg_rating
    }), 200


@competition_bp.route('/<int:comp_id>/feedback', methods=['POST'])
@require_auth
def submit_event_feedback(comp_id):
    from app.models import ClubEventFeedback
    comp = Competition.query.get_or_404(comp_id)
    data = request.get_json() or {}

    try:
        rating = int(data.get('rating', 5))
    except (ValueError, TypeError):
        rating = 5

    if rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5 stars'}), 400

    feedback_text = (data.get('feedback_text') or data.get('comment') or '').strip()

    existing = ClubEventFeedback.query.filter_by(competition_id=comp_id, user_id=g.current_user.id).first()
    if existing:
        existing.rating = rating
        existing.feedback_text = feedback_text
        existing.created_at = datetime.utcnow()
    else:
        fb = ClubEventFeedback(
            competition_id=comp_id,
            user_id=g.current_user.id,
            rating=rating,
            feedback_text=feedback_text
        )
        db.session.add(fb)

    db.session.commit()
    log_audit('SUBMIT_EVENT_FEEDBACK', target_type='Competition', target_id=comp_id)

    return jsonify({'message': 'Thank you for your event feedback!', 'feedback': (existing or fb).to_dict()}), 200


@competition_bp.route('/<int:comp_id>/feedback/export', methods=['GET'])
@require_role('teacher', 'admin', 'root_admin')
def export_event_feedback(comp_id):
    from app.models import ClubEventFeedback
    comp = Competition.query.get_or_404(comp_id)
    feedbacks = ClubEventFeedback.query.filter_by(competition_id=comp_id).order_by(ClubEventFeedback.created_at.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Badge ID', 'Full Name', 'Username', 'Email', 'Rating (1-5)', 'Feedback', 'Submitted At'
    ])

    for fb in feedbacks:
        u = User.query.get(fb.user_id)
        writer.writerow([
            u.get_badge_id() if u else 'N/A',
            u.full_name if u else (u.username if u else 'Unknown'),
            u.username if u else 'Unknown',
            u.email if u else 'N/A',
            fb.rating,
            fb.feedback_text or '',
            fb.created_at.isoformat() if fb.created_at else ''
        ])

    csv_data = output.getvalue()
    response = make_response(csv_data)
    filename = f"club_event_feedback_{comp_id}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    return response
