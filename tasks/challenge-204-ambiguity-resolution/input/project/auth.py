"""Authentication utilities for the blog application."""

import hashlib
import hmac
import time
from typing import Optional, Tuple

from config import Config
from models import User
from database import Database
from utils import verify_password


# Simple token store (maps token -> user_id)
_active_tokens = {}


def login(db: Database, email: str, password: str) -> Optional[str]:
    """Authenticate a user and return a session token, or None."""
    user = db.get_user_by_email(email)
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    token = _generate_token(user.id)
    _active_tokens[token] = user.id
    return token


def logout(token: str) -> bool:
    """Invalidate a session token."""
    return _active_tokens.pop(token, None) is not None


def get_current_user(db: Database, token: str) -> Optional[User]:
    """Return the User associated with the token, or None."""
    user_id = _active_tokens.get(token)
    if user_id is None:
        return None
    return db.get_user(user_id)


def _generate_token(user_id: str) -> str:
    """Create a simple HMAC-based token."""
    payload = f"{user_id}:{time.time()}"
    sig = hmac.new(
        Config.SECRET_KEY.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    return f"{payload}:{sig}"
