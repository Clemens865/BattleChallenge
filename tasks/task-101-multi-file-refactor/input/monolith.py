"""
Monolithic user registration system.
Handles data models, validation, database operations, and API endpoints
all in a single file.
"""
import hashlib
import json
import re
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone


# ============ MODELS ============

@dataclass
class User:
    id: str
    email: str
    username: str
    password_hash: str
    created_at: str
    is_active: bool = True


@dataclass
class RegistrationRequest:
    email: str
    username: str
    password: str


@dataclass
class RegistrationResponse:
    success: bool
    message: str
    user_id: str = ""


@dataclass
class APIResponse:
    status_code: int
    body: dict = field(default_factory=dict)


# ============ VALIDATORS ============

def validate_email(email: str) -> tuple:
    """Validate email format. Returns (is_valid, error_message)."""
    if not email or not isinstance(email, str):
        return (False, "Email is required")
    email = email.strip()
    if len(email) > 254:
        return (False, "Email too long")
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return (False, "Invalid email format")
    local, domain = email.rsplit('@', 1)
    if local.startswith('.') or local.endswith('.') or '..' in local:
        return (False, "Invalid local part")
    if domain.startswith('-') or domain.endswith('-'):
        return (False, "Invalid domain")
    return (True, "")


def validate_password(password: str) -> tuple:
    """Validate password strength. Returns (is_valid, error_message)."""
    if not password or not isinstance(password, str):
        return (False, "Password is required")
    if len(password) < 8:
        return (False, "Password must be at least 8 characters")
    if len(password) > 128:
        return (False, "Password too long")
    if not re.search(r'[A-Z]', password):
        return (False, "Password must contain an uppercase letter")
    if not re.search(r'[a-z]', password):
        return (False, "Password must contain a lowercase letter")
    if not re.search(r'[0-9]', password):
        return (False, "Password must contain a digit")
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?/~`]', password):
        return (False, "Password must contain a special character")
    return (True, "")


def validate_username(username: str) -> tuple:
    """Validate username. Returns (is_valid, error_message)."""
    if not username or not isinstance(username, str):
        return (False, "Username is required")
    username = username.strip()
    if len(username) < 3:
        return (False, "Username must be at least 3 characters")
    if len(username) > 20:
        return (False, "Username must be at most 20 characters")
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return (False, "Username can only contain letters, digits, and underscores")
    if username[0].isdigit():
        return (False, "Username cannot start with a digit")
    return (True, "")


# ============ DATABASE ============

class UserDatabase:
    """In-memory user database."""

    def __init__(self):
        self._users = {}

    def add_user(self, user: User) -> bool:
        """Add a user. Returns False if user ID already exists."""
        if user.id in self._users:
            return False
        self._users[user.id] = user
        return True

    def get_user(self, user_id: str):
        """Get user by ID. Returns None if not found."""
        return self._users.get(user_id)

    def get_user_by_email(self, email: str):
        """Get user by email. Returns None if not found."""
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def get_user_by_username(self, username: str):
        """Get user by username. Returns None if not found."""
        for user in self._users.values():
            if user.username == username:
                return user
        return None

    def delete_user(self, user_id: str) -> bool:
        """Delete a user. Returns False if not found."""
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False

    def list_users(self) -> list:
        """List all users."""
        return list(self._users.values())

    def update_user(self, user_id: str, **kwargs):
        """Update user fields. Returns updated user or None."""
        user = self._users.get(user_id)
        if user is None:
            return None
        for key, value in kwargs.items():
            if hasattr(user, key) and key != 'id':
                setattr(user, key, value)
        return user


# ============ HELPERS ============

def _hash_password(password: str, email: str) -> str:
    """Hash password using SHA-256 with email-derived salt."""
    salt = hashlib.sha256(email.encode()).hexdigest()[:8]
    salted = salt + password
    return hashlib.sha256(salted.encode()).hexdigest()


def _make_user_dict(user: User) -> dict:
    """Convert user to a safe dict (no password hash)."""
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "created_at": user.created_at,
        "is_active": user.is_active,
    }


# ============ API ENDPOINTS ============

def register_user(request_json: str, db: UserDatabase) -> str:
    """Register a new user. Returns JSON response string."""
    try:
        data = json.loads(request_json)
    except (json.JSONDecodeError, TypeError):
        resp = APIResponse(
            status_code=400,
            body={"success": False, "message": "Invalid JSON"}
        )
        return json.dumps(asdict(resp), sort_keys=True)

    email = data.get("email", "")
    username = data.get("username", "")
    password = data.get("password", "")

    # Validate email
    valid, msg = validate_email(email)
    if not valid:
        resp = APIResponse(status_code=400, body={"success": False, "message": msg})
        return json.dumps(asdict(resp), sort_keys=True)

    # Validate username
    valid, msg = validate_username(username)
    if not valid:
        resp = APIResponse(status_code=400, body={"success": False, "message": msg})
        return json.dumps(asdict(resp), sort_keys=True)

    # Validate password
    valid, msg = validate_password(password)
    if not valid:
        resp = APIResponse(status_code=400, body={"success": False, "message": msg})
        return json.dumps(asdict(resp), sort_keys=True)

    # Check duplicates
    if db.get_user_by_email(email):
        resp = APIResponse(status_code=409, body={"success": False, "message": "Email already registered"})
        return json.dumps(asdict(resp), sort_keys=True)

    if db.get_user_by_username(username):
        resp = APIResponse(status_code=409, body={"success": False, "message": "Username already taken"})
        return json.dumps(asdict(resp), sort_keys=True)

    # Create user
    user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, email))
    password_hash = _hash_password(password, email)
    now = datetime.now(timezone.utc).isoformat()

    user = User(
        id=user_id,
        email=email,
        username=username,
        password_hash=password_hash,
        created_at=now,
    )

    db.add_user(user)

    resp = APIResponse(
        status_code=201,
        body={"success": True, "message": "User registered successfully", "user_id": user_id}
    )
    return json.dumps(asdict(resp), sort_keys=True)


def get_user_endpoint(user_id: str, db: UserDatabase) -> str:
    """Get user by ID. Returns JSON response string."""
    user = db.get_user(user_id)
    if user is None:
        resp = APIResponse(status_code=404, body={"success": False, "message": "User not found"})
        return json.dumps(asdict(resp), sort_keys=True)

    resp = APIResponse(status_code=200, body={"success": True, "user": _make_user_dict(user)})
    return json.dumps(asdict(resp), sort_keys=True)


def delete_user_endpoint(user_id: str, db: UserDatabase) -> str:
    """Delete user by ID. Returns JSON response string."""
    if db.delete_user(user_id):
        resp = APIResponse(status_code=200, body={"success": True, "message": "User deleted"})
    else:
        resp = APIResponse(status_code=404, body={"success": False, "message": "User not found"})
    return json.dumps(asdict(resp), sort_keys=True)


def list_users_endpoint(db: UserDatabase) -> str:
    """List all users. Returns JSON response string."""
    users = [_make_user_dict(u) for u in db.list_users()]
    resp = APIResponse(status_code=200, body={"success": True, "users": users, "count": len(users)})
    return json.dumps(asdict(resp), sort_keys=True)
