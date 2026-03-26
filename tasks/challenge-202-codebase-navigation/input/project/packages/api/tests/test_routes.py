"""Basic tests for API routes."""

import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from packages.core.src.database import db
from packages.core.src.config import set_config, reset_config


def setup_function():
    db.clear_table("users")
    db.clear_table("teams")
    set_config("AUTH_ENABLED", False)


def teardown_function():
    reset_config()


def _make_app():
    from packages.api.src.app import Application
    return Application()


def test_health_check():
    app = _make_app()
    result = app.handle_request("GET", "/api/health")
    assert result["status"] == 200
    assert result["data"]["status"] == "healthy"


def test_create_user():
    app = _make_app()
    result = app.handle_request("POST", "/api/users", body={
        "name": "Alice", "email": "alice@example.com",
    })
    assert result["status"] == 201
    assert result["data"]["name"] == "Alice"


def test_list_users():
    app = _make_app()
    app.handle_request("POST", "/api/users", body={
        "name": "Bob", "email": "bob@example.com",
    })
    result = app.handle_request("GET", "/api/users")
    assert result["status"] == 200
    assert result["total"] >= 1


def test_create_team():
    app = _make_app()
    result = app.handle_request("POST", "/api/teams", body={
        "name": "Engineering",
    })
    assert result["status"] == 201


def test_not_found():
    app = _make_app()
    result = app.handle_request("GET", "/api/nonexistent")
    assert result["status"] == 404
