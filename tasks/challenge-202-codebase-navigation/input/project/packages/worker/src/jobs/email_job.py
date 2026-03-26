"""Email sending job handler."""

from ....core.src.logger import get_logger
from ....core.src.config import get_config

logger = get_logger("email_job")


def handle_send_email(payload: dict) -> dict:
    """Process a send-email job."""
    to = payload.get("to")
    subject = payload.get("subject", "No subject")
    body = payload.get("body", "")
    if not to:
        raise ValueError("Email recipient is required")
    # In production this would use an SMTP library
    logger.info(f"Sending email to {to}: {subject}")
    return {
        "sent": True,
        "to": to,
        "subject": subject,
        "body_length": len(body),
    }


def handle_send_bulk_email(payload: dict) -> dict:
    """Process a bulk email job."""
    recipients = payload.get("recipients", [])
    subject = payload.get("subject", "No subject")
    results = []
    for recipient in recipients:
        results.append(handle_send_email({
            "to": recipient,
            "subject": subject,
            "body": payload.get("body", ""),
        }))
    return {"sent_count": len(results), "results": results}
