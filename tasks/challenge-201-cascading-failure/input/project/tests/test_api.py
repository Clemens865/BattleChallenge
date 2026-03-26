"""Tests for the book library API handlers."""

import pytest
from ..api_handlers import (
    handle_list_books,
    handle_get_book,
    handle_create_book,
    handle_delete_book,
    reset_db,
    get_db,
)
from ..models import Book
from datetime import date


@pytest.fixture(autouse=True)
def clean_db():
    reset_db()
    yield
    reset_db()


def _sample_book_data():
    return {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "isbn": "978-0743273565",
        "published_date": "1925-04-10",
        "genre": "Fiction",
        "pages": 180,
    }


def test_create_book():
    result = handle_create_book(_sample_book_data())
    assert result["status"] == 201
    assert result["data"]["title"] == "The Great Gatsby"
    assert result["data"]["published_date"] == "1925-04-10"


def test_create_book_invalid():
    result = handle_create_book({"title": ""})
    assert result["status"] == 400
    assert len(result["errors"]) > 0


def test_list_books():
    handle_create_book(_sample_book_data())
    result = handle_list_books()
    assert result["status"] == 200
    assert result["count"] == 1
    assert result["data"][0]["published_date"] == "1925-04-10"


def test_list_books_empty():
    result = handle_list_books()
    assert result["status"] == 200
    assert result["count"] == 0


def test_get_book():
    created = handle_create_book(_sample_book_data())
    book_id = created["data"]["id"]
    result = handle_get_book(book_id)
    assert result["status"] == 200
    assert result["data"]["isbn"] == "978-0743273565"
    assert result["data"]["published_date"] == "1925-04-10"


def test_get_book_not_found():
    result = handle_get_book("nonexistent-id")
    assert result["status"] == 404


def test_delete_book():
    created = handle_create_book(_sample_book_data())
    book_id = created["data"]["id"]
    result = handle_delete_book(book_id)
    assert result["status"] == 204


def test_delete_book_not_found():
    result = handle_delete_book("nonexistent-id")
    assert result["status"] == 404


def test_filter_by_author():
    handle_create_book(_sample_book_data())
    handle_create_book({
        "title": "1984",
        "author": "George Orwell",
        "isbn": "978-0451524935",
        "published_date": "1949-06-08",
    })
    result = handle_list_books({"author": "George Orwell"})
    assert result["count"] == 1
    assert result["data"][0]["author"] == "George Orwell"


def test_filter_by_genre():
    handle_create_book(_sample_book_data())
    result = handle_list_books({"genre": "Fiction"})
    assert result["count"] == 1


def test_duplicate_isbn():
    handle_create_book(_sample_book_data())
    result = handle_create_book(_sample_book_data())
    assert result["status"] == 409
