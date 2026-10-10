"""Email-only notification dispatcher for CampusSlot."""
from flask import current_app
from app.services.email_service import send_appointment_email, send_registration_email
from app import db
from app.models.notification_log import NotificationLog


def notify_appointment(appointment, event="confirmed"):
    result = {"email": {"sent": 0, "attempted": 0, "errors": []}}
    try:
        result["email"] = send_appointment_email(appointment, event)
    except Exception as exc:
        result["email"]["errors"] = [str(exc)]
        current_app.logger.exception("CampusSlot email dispatcher failed | appointment=%s | event=%s", appointment.tracking_id, event)
    try:
        channel_result = result["email"]
        errors = channel_result.get("errors") or []
        attempted = int(channel_result.get("attempted") or 0)
        sent = int(channel_result.get("sent") or 0)
        status = "sent" if sent else ("failed" if errors else "skipped")
        db.session.add(NotificationLog(
            appointment_id=appointment.id, channel="email",
            recipient="multiple" if attempted > 1 else "configured-recipient",
            event=event, status=status,
            error_message=" | ".join(errors[:5]) if errors else None,
            attempt_count=max(attempted, 1),
        ))
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("CampusSlot email audit logging failed | appointment=%s | event=%s", appointment.tracking_id, event)
    current_app.logger.info("CampusSlot EMAIL RESULT | appointment=%s | event=%s | email=%s/%s", appointment.tracking_id, event, result["email"]["sent"], result["email"]["attempted"])
    return result


def notify_registration(record, event="submitted"):
    try:
        return {"email": send_registration_email(record, event)}
    except Exception as exc:
        current_app.logger.exception("CampusSlot registration email failed | registration=%s | event=%s", getattr(record, "registration_id", None), event)
        return {"email": {"sent": 0, "attempted": 1, "errors": [str(exc)]}}
