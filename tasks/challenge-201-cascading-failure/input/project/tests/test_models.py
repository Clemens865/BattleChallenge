"""Tests for the book models and serializers."""

import pytest
from datetime import date
from ..models import Book, BookCollection
from ..serializers import serialize_book, deserialize_book, serialize_book_list


def test_book_creation():
    book = Book(
        title="Test Book",
        author="Test Author",
        isbn="978-0000000001",
        published_date=date(2023, 1, 15),
    )
    assert book.title == "Test Book"
    assert book.published_date == date(2023, 1, 15)


def test_book_from_string_date():
    book = Book(
        title="Test",
        author="Author",
        isbn="978-0000000002",
        published_date="2023-06-15",
    )
    assert isinstance(book.published_date, date)
    assert book.published_date.year == 2023


def test_book_requires_isbn():
    with pytest.raises(ValueError):
        Book(title="No ISBN", author="Author", isbn="", published_date=date.today())


def test_serialize_book():
    book = Book(
        title="Serialize Me",
        author="Author",
        isbn="978-0000000003",
        published_date=date(2020, 3, 14),
        genre="Science",
        pages=300,
    )
    data = serialize_book(book)
    assert data["title"] == "Serialize Me"
    assert data["published_date"] == "2020-03-14"
    assert data["pages"] == 300


def test_deserialize_book():
    data = {
        "title": "Deserialized",
        "author": "Author",
        "isbn": "978-0000000004",
        "published_date": "2021-07-04",
        "genre": "History",
        "pages": 250,
    }
    book = deserialize_book(data)
    assert book.title == "Deserialized"
    assert isinstance(book.published_date, date)


def test_serialize_roundtrip():
    book = Book(
        title="Roundtrip",
        author="Author",
        isbn="978-0000000005",
        published_date=date(2022, 12, 25),
    )
    data = serialize_book(book)
    book2 = deserialize_book(data)
    assert book.title == book2.title
    assert book.isbn == book2.isbn


def test_collection_add():
    coll = BookCollection(name="test")
    book = Book(title="A", author="B", isbn="978-0000000006", published_date=date.today())
    coll.add_book(book)
    assert len(coll.books) == 1


def test_collection_duplicate():
    coll = BookCollection(name="test")
    book = Book(title="A", author="B", isbn="978-0000000007", published_date=date.today())
    coll.add_book(book)
    with pytest.raises(ValueError):
        coll.add_book(Book(title="C", author="D", isbn="978-0000000007", published_date=date.today()))


def test_serialize_book_list():
    books = [
        Book(title="A", author="X", isbn="978-0000000008", published_date=date(2023, 1, 1)),
        Book(title="B", author="Y", isbn="978-0000000009", published_date=date(2023, 6, 1)),
    ]
    result = serialize_book_list(books)
    assert len(result) == 2
    assert result[0]["published_date"] == "2023-01-01"
    assert result[1]["published_date"] == "2023-06-01"
