"""API route handlers for users and posts."""

import json
from typing import Tuple

from models import User, Post
from database import Database
from auth import login, logout, get_current_user
from utils import generate_id, hash_password, get_timestamp, validate_email_format


def create_user(db: Database, data: dict) -> Tuple[dict, int]:
    """Register a new user."""
    email = data.get("email", "")
    username = data.get("username", "")
    password = data.get("password", "")

    if not validate_email_format(email):
        return {"error": "Invalid email format"}, 400
    if len(username) < 3:
        return {"error": "Username must be at least 3 characters"}, 400
    if len(password) < 6:
        return {"error": "Password must be at least 6 characters"}, 400
    if db.get_user_by_email(email) is not None:
        return {"error": "Email already registered"}, 409

    user = User(
        id=generate_id(),
        username=username,
        email=email,
        password_hash=hash_password(password),
    )
    db.add_user(user)
    return {"user": user.to_dict(), "message": "User created"}, 201


def create_post(db: Database, author_id: str, data: dict) -> Tuple[dict, int]:
    """Create a new blog post."""
    title = data.get("title", "")
    body = data.get("body", "")
    tags = data.get("tags", [])

    if not title or len(title) < 5:
        return {"error": "Title must be at least 5 characters"}, 400
    if not body:
        return {"error": "Body is required"}, 400

    author = db.get_user(author_id)
    if author is None:
        return {"error": "Author not found"}, 404

    post = Post(
        id=generate_id(),
        title=title,
        body=body,
        author_id=author_id,
        tags=tags,
    )
    db.add_post(post)
    return {"post": post.to_dict(), "message": "Post created"}, 201


def get_posts(db: Database) -> Tuple[dict, int]:
    """List all published posts."""
    posts = db.list_posts(published_only=True)
    return {"posts": [p.to_dict() for p in posts], "count": len(posts)}, 200
