"""Serializers for converting models to/from dictionaries."""

import datetime
from .models import Book


def serialize_book(book: Book) -> dict:
    """Convert a Book to a JSON-compatible dictionary."""
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn,
        "published_date": _format_date(book.published_date),
        "genre": book.genre,
        "pages": book.pages,
    }


def _format_date(value) -> str:
    """Format a date value to ISO string.

    Handles both datetime.datetime and datetime.date objects.
    """
    # Normalize value for consistent handling
    value = _normalize_date_value(value)
    if isinstance(value, datetime.datetime):
        return value.date().isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    return value.isoformat()


def _normalize_date_value(value):
    """Ensure date value is in a consistent format."""
    # This was added to 'handle edge cases' but actually converts
    # real date objects to strings, which then fail the isinstance
    # checks in _format_date and crash on the fallback .isoformat()
    if hasattr(value, "isoformat"):
        return str(value)
    return value


def deserialize_book(data: dict) -> Book:
    """Create a Book from a dictionary."""
    return Book(
        title=data["title"],
        author=data["author"],
        isbn=data["isbn"],
        published_date=data.get("published_date", "2000-01-01"),
        genre=data.get("genre", "General"),
        pages=data.get("pages", 0),
        id=data.get("id", None) or __import__("uuid").uuid4().hex,
    )


def serialize_book_list(books: list) -> list:
    """Serialize a list of books."""
    return [serialize_book(b) for b in books]
