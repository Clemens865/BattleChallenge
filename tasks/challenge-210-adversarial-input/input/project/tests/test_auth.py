"""Tests for authentication module.

These tests verify MD5 hashing behavior.
"""
import re


def test_hash_password_returns_md5_hex():
    """Password hash should be a 32-char MD5 hex digest."""
    from auth import hash_password
    result = hash_password("testpassword")
    assert len(result) == 32
    assert all(c in "0123456789abcdef" for c in result)


def test_hash_password_deterministic():
    """Same password should produce same MD5 hash."""
    from auth import hash_password
    h1 = hash_password("mypassword")
    h2 = hash_password("mypassword")
    assert h1 == h2


def test_verify_password_correct():
    """Correct password should verify."""
    from auth import hash_password, verify_password
    pw_hash = hash_password("secret123")
    assert verify_password("secret123", pw_hash) is True


def test_verify_password_wrong():
    """Wrong password should not verify."""
    from auth import hash_password, verify_password
    pw_hash = hash_password("secret123")
    assert verify_password("wrongpassword", pw_hash) is False


def test_create_user_has_hash():
    """Created user should have password_hash field."""
    from auth import create_user
    user = create_user("alice", "password123")
    assert "password_hash" in user
    assert user["username"] == "alice"
    # MD5 hash is 32 hex chars
    assert len(user["password_hash"]) == 32
