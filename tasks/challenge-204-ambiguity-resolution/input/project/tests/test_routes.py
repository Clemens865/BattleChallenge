"""Tests for the blog application route handlers."""

import sys
import os

# Ensure project root is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import Database
from routes import create_user, create_post, get_posts
from utils import generate_id, hash_password
from models import User


def _make_db_with_user():
    """Helper: create a Database with one registered user."""
    db = Database()
    user = User(
        id="user-001",
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("secret123"),
    )
    db.add_user(user)
    return db, user


def test_create_user_success():
    db = Database()
    result, status = create_user(db, {
        "email": "alice@example.com",
        "username": "alice",
        "password": "strongpass",
    })
    assert status == 201
    assert "user" in result
    assert result["user"]["email"] == "alice@example.com"


def test_create_user_invalid_email():
    db = Database()
    result, status = create_user(db, {
        "email": "not-an-email",
        "username": "bob",
        "password": "strongpass",
    })
    assert status == 400


def test_create_user_duplicate_email():
    db, _ = _make_db_with_user()
    result, status = create_user(db, {
        "email": "test@example.com",
        "username": "other",
        "password": "strongpass",
    })
    assert status == 409


def test_create_post_success():
    db, user = _make_db_with_user()
    result, status = create_post(db, user.id, {
        "title": "Hello World Post",
        "body": "This is the body of my first post.",
        "tags": ["tech"],
    })
    assert status == 201
    assert result["post"]["author_id"] == user.id


def test_create_post_missing_title():
    db, user = _make_db_with_user()
    result, status = create_post(db, user.id, {"title": "", "body": "content"})
    assert status == 400


def test_create_post_unknown_author():
    db = Database()
    result, status = create_post(db, "nonexistent", {
        "title": "Orphan Post Title",
        "body": "No author exists for this.",
    })
    assert status == 404


def test_get_posts_empty():
    db = Database()
    result, status = get_posts(db)
    assert status == 200
    assert result["count"] == 0
