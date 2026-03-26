"""User CRUD routes."""

from ....core.src.database import db
from ....core.src.helpers import generate_id, timestamp_iso
from ....core.src.validators import validate_email, validate_required
from ....core.src.serializers import paginate


def register(router):
    """Register user routes on the router."""
    router.add_route("GET", "/api/users", list_users)
    router.add_route("POST", "/api/users", create_user)
    router.add_route("GET", "/api/users/{user_id}", get_user)
    router.add_route("DELETE", "/api/users/{user_id}", delete_user)


def list_users(request: dict) -> dict:
    """GET /api/users — list all users with pagination."""
    users = db.get_all("users")
    page = int(request.get("body", {}).get("page", 1))
    result = paginate(users, page=page)
    return {"status": 200, **result}


def create_user(request: dict) -> dict:
    """POST /api/users — create a new user."""
    body = request.get("body", {})
    errors = validate_required(body, ["name", "email"])
    if errors:
        return {"status": 400, "errors": errors}
    if not validate_email(body["email"]):
        return {"status": 400, "errors": ["Invalid email format"]}
    # Check for duplicate email
    existing = db.get_all("users")
    if any(u["email"] == body["email"] for u in existing):
        return {"status": 409, "error": "Email already registered"}
    user = {
        "id": generate_id(),
        "name": body["name"],
        "email": body["email"],
        "role": body.get("role", "member"),
        "created_at": timestamp_iso(),
    }
    db.insert("users", user["id"], user)
    return {"status": 201, "data": user}


def get_user(request: dict) -> dict:
    """GET /api/users/:id — get a single user."""
    user_id = request["params"]["user_id"]
    user = db.get("users", user_id)
    if user is None:
        return {"status": 404, "error": "User not found"}
    return {"status": 200, "data": user}


def delete_user(request: dict) -> dict:
    """DELETE /api/users/:id — delete a user."""
    user_id = request["params"]["user_id"]
    if db.delete("users", user_id):
        return {"status": 204}
    return {"status": 404, "error": "User not found"}
