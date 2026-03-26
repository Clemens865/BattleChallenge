"""Shared validation utilities."""

import re


def validate_email(email: str) -> bool:
    """Basic email format validation."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_required(data: dict, fields: list) -> list:
    """Check that all required fields are present and non-empty."""
    errors = []
    for field in fields:
        if not data.get(field):
            errors.append(f"{field} is required")
    return errors


def validate_string_length(value: str, min_len: int = 1, max_len: int = 255) -> bool:
    """Check string length bounds."""
    if not isinstance(value, str):
        return False
    return min_len <= len(value) <= max_len


def validate_positive_int(value) -> bool:
    """Check that value is a positive integer."""
    try:
        return int(value) > 0
    except (ValueError, TypeError):
        return False
