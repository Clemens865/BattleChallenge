"""Shared utility functions."""

import hashlib
import uuid
from datetime import datetime


def generate_id() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 (simplified for demo)."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(password) == password_hash


def get_timestamp() -> str:
    """Return the current UTC timestamp as ISO string."""
    return datetime.utcnow().isoformat()


def truncate_string(text: str, max_length: int = 100) -> str:
    """Truncate a string to max_length, adding ellipsis if needed."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def validate_email_format(email: str) -> bool:
    """Basic email format validation."""
    if not email or "@" not in email:
        return False
    local, domain = email.rsplit("@", 1)
    return len(local) > 0 and "." in domain and len(domain) > 2
