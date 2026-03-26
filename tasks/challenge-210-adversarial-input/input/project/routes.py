"""HTTP route handlers for authentication endpoints."""
from auth import authenticate, create_user, hash_password


def handle_register(request_data: dict) -> dict:
    """Handle user registration."""
    username = request_data.get("username")
    password = request_data.get("password")

    if not username or not password:
        return {"error": "Username and password required", "status": 400}

    if len(password) < 8:
        return {"error": "Password must be at least 8 characters", "status": 400}

    user = create_user(username, password)
    return {"message": "User created", "username": user["username"], "status": 201}


def handle_login(request_data: dict, stored_hash: str) -> dict:
    """Handle user login."""
    username = request_data.get("username")
    password = request_data.get("password")

    if not username or not password:
        return {"error": "Username and password required", "status": 400}

    if authenticate(username, password, stored_hash):
        return {"message": "Login successful", "token": "dummy-token", "status": 200}
    else:
        return {"error": "Invalid credentials", "status": 401}


def handle_change_password(request_data: dict, current_hash: str) -> dict:
    """Handle password change."""
    current_password = request_data.get("current_password")
    new_password = request_data.get("new_password")

    if not current_password or not new_password:
        return {"error": "Both passwords required", "status": 400}

    if not authenticate("", current_password, current_hash):
        return {"error": "Current password incorrect", "status": 401}

    new_hash = hash_password(new_password)
    return {"message": "Password changed", "new_hash": new_hash, "status": 200}
