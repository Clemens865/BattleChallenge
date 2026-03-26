"""Notification job handler."""

from ....core.src.logger import get_logger

logger = get_logger("notification_job")


def handle_push_notification(payload: dict) -> dict:
    """Send a push notification."""
    user_id = payload.get("user_id")
    message = payload.get("message", "")
    if not user_id:
        raise ValueError("user_id is required")
    logger.info(f"Push notification to {user_id}: {message[:50]}")
    return {"delivered": True, "user_id": user_id}


def handle_in_app_notification(payload: dict) -> dict:
    """Create an in-app notification."""
    user_id = payload.get("user_id")
    title = payload.get("title", "Notification")
    body = payload.get("body", "")
    if not user_id:
        raise ValueError("user_id is required")
    return {
        "created": True,
        "user_id": user_id,
        "title": title,
        "body_length": len(body),
    }
