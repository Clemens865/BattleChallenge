"""API handler functions for the book library."""

from .database import Database
from .models import Book
from .serializers import serialize_book, serialize_book_list, deserialize_book
from .validators import validate_book_data

# Global database instance
_db = Database()


def get_db() -> Database:
    return _db


def reset_db() -> None:
    global _db
    _db = Database()


def handle_list_books(query_params: dict = None) -> dict:
    """Handle GET /books — list all books."""
    db = get_db()
    books = db.get_all()
    if query_params and query_params.get("author"):
        books = [b for b in books if b.author.lower() == query_params["author"].lower()]
    if query_params and query_params.get("genre"):
        books = [b for b in books if b.genre.lower() == query_params["genre"].lower()]
    return {
        "status": 200,
        "data": serialize_book_list(books),
        "count": len(books),
    }


def handle_get_book(book_id: str) -> dict:
    """Handle GET /books/:id — get a single book."""
    db = get_db()
    book = db.get_by_id(book_id)
    if book is None:
        return {"status": 404, "error": "Book not found"}
    # Line 45: This calls serialize_book which calls _format_date
    # The error surfaces HERE but the root cause is in serializers.py
    return {"status": 200, "data": serialize_book(book)}


def handle_create_book(data: dict) -> dict:
    """Handle POST /books — create a new book."""
    errors = validate_book_data(data)
    if errors:
        return {"status": 400, "errors": errors}
    db = get_db()
    try:
        book = deserialize_book(data)
        db.insert(book)
        return {"status": 201, "data": serialize_book(book)}
    except ValueError as e:
        return {"status": 409, "error": str(e)}


def handle_delete_book(book_id: str) -> dict:
    """Handle DELETE /books/:id — delete a book."""
    db = get_db()
    if db.delete(book_id):
        return {"status": 204}
    return {"status": 404, "error": "Book not found"}
