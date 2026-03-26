"""Utility functions for the book library."""

import hashlib
import re


def generate_slug(title: str) -> str:
    """Generate a URL-friendly slug from a book title."""
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug.strip("-")


def truncate(text: str, max_length: int = 100) -> str:
    """Truncate text to max_length, adding ellipsis if needed."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def compute_checksum(data: str) -> str:
    """Compute SHA-256 checksum of a string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def sanitize_input(value: str) -> str:
    """Basic input sanitization."""
    if not isinstance(value, str):
        return str(value)
    return value.strip().replace("\x00", "")
