"""Utility functions for the authentication system."""
import re
import secrets
import string
from config import MIN_PASSWORD_LENGTH, REQUIRE_UPPERCASE, REQUIRE_DIGIT


def validate_password(password: str) -> tuple:
    """Validate password against policy.

    Returns:
        (is_valid, error_message)
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"

    if REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if REQUIRE_DIGIT and not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    return True, None


def generate_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def sanitize_username(username: str) -> str:
    """Sanitize a username — allow only alphanumeric and underscores."""
    return re.sub(r"[^\w]", "", username)


def mask_email(email: str) -> str:
    """Mask an email for display: john@example.com -> j***@example.com"""
    if "@" not in email:
        return email
    local, domain = email.split("@", 1)
    if len(local) <= 1:
        return f"{local}***@{domain}"
    return f"{local[0]}***@{domain}"
