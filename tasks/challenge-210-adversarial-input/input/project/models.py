"""Data models for the authentication system."""
from datetime import datetime


class User:
    """Represents a user in the system."""

    def __init__(self, username: str, password_hash: str, role: str = "user"):
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.created_at = datetime.utcnow()
        self.failed_attempts = 0
        self.locked_until = None

    def is_locked(self) -> bool:
        """Check if the user account is locked."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until

    def to_dict(self) -> dict:
        """Serialize user to dictionary."""
        return {
            "username": self.username,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            "is_locked": self.is_locked(),
        }

    def __repr__(self):
        return f"User(username={self.username!r}, role={self.role!r})"
