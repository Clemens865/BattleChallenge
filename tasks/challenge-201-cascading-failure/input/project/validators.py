"""Input validation for API requests."""

import re
from datetime import date


def validate_isbn(isbn: str) -> bool:
    """Validate ISBN-10 or ISBN-13 format."""
    cleaned = isbn.replace("-", "").replace(" ", "")
    if len(cleaned) == 10:
        return bool(re.match(r"^\d{9}[\dXx]$", cleaned))
    if len(cleaned) == 13:
        return bool(re.match(r"^\d{13}$", cleaned))
    return False


def validate_book_data(data: dict) -> list:
    """Validate book creation data, return list of errors."""
    errors = []
    if not data.get("title"):
        errors.append("Title is required")
    if not data.get("author"):
        errors.append("Author is required")
    if not data.get("isbn"):
        errors.append("ISBN is required")
    elif not validate_isbn(data["isbn"]):
        errors.append("Invalid ISBN format")
    if data.get("published_date"):
        try:
            date.fromisoformat(data["published_date"])
        except (ValueError, TypeError):
            errors.append("Invalid date format. Use YYYY-MM-DD")
    if data.get("pages") is not None:
        try:
            p = int(data["pages"])
            if p < 0:
                errors.append("Pages must be non-negative")
        except (ValueError, TypeError):
            errors.append("Pages must be a number")
    return errors
