"""Route definitions for the book library API."""

from .api_handlers import (
    handle_list_books,
    handle_get_book,
    handle_create_book,
    handle_delete_book,
)


ROUTES = {
    ("GET", "/books"): handle_list_books,
    ("GET", "/books/{id}"): handle_get_book,
    ("POST", "/books"): handle_create_book,
    ("DELETE", "/books/{id}"): handle_delete_book,
}


def dispatch(method: str, path: str, data: dict = None, params: dict = None) -> dict:
    """Simple router that dispatches to the correct handler."""
    # Check for parameterized routes
    parts = path.strip("/").split("/")
    if len(parts) == 2 and parts[0] == "books":
        book_id = parts[1]
        if method == "GET":
            return handle_get_book(book_id)
        elif method == "DELETE":
            return handle_delete_book(book_id)

    # Check for exact matches
    handler = ROUTES.get((method, path))
    if handler is None:
        return {"status": 404, "error": "Route not found"}

    if method == "POST":
        return handler(data or {})
    elif method == "GET":
        return handler(params or {})
    return handler()
