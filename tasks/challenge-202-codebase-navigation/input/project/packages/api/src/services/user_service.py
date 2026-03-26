"""User business logic service."""

from ....core.src.base import BaseService
from ....core.src.database import db
from ....core.src.crypto import hash_password, verify_password
from ....core.src.helpers import generate_id, timestamp_iso


class UserService(BaseService):
    """Handles user-related business logic."""

    def __init__(self):
        super().__init__("UserService")

    def create_user(self, name: str, email: str, password: str = None) -> dict:
        """Create a new user with optional password hashing."""
        user = {
            "id": generate_id(),
            "name": name,
            "email": email,
            "created_at": timestamp_iso(),
        }
        if password:
            hashed, salt = hash_password(password)
            user["password_hash"] = hashed
            user["password_salt"] = salt
        db.insert("users", user["id"], user)
        self.log_info(f"Created user: {email}")
        return user

    def authenticate(self, email: str, password: str) -> dict:
        """Authenticate a user by email and password."""
        users = db.get_all("users")
        for user in users:
            if user["email"] == email:
                if verify_password(password, user.get("password_hash", ""), user.get("password_salt", "")):
                    return user
        return None

    def get_user_count(self) -> int:
        return db.count("users")
