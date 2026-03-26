"""Cryptographic utilities."""

import hashlib
import hmac
import secrets
from .config import get_config


def hash_password(password: str, salt: str = None) -> tuple:
    """Hash a password with SHA-256 and a random salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return hashed, salt


def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify a password against its hash."""
    computed, _ = hash_password(password, salt)
    return hmac.compare_digest(computed, hashed)


def generate_token() -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)


def sign_data(data: str) -> str:
    """Sign data with the app secret key."""
    key = get_config("SECRET_KEY", "default-key")
    return hmac.new(key.encode(), data.encode(), hashlib.sha256).hexdigest()
