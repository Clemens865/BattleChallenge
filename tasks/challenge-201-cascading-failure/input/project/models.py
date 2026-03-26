"""Data models for the book library."""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional
import uuid


@dataclass
class Book:
    title: str
    author: str
    isbn: str
    published_date: date
    genre: str = "General"
    pages: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        if isinstance(self.published_date, str):
            self.published_date = date.fromisoformat(self.published_date)
        if not self.isbn:
            raise ValueError("ISBN is required")


@dataclass
class BookCollection:
    name: str
    books: list = field(default_factory=list)

    def add_book(self, book: Book) -> None:
        if any(b.isbn == book.isbn for b in self.books):
            raise ValueError(f"Book with ISBN {book.isbn} already exists")
        self.books.append(book)

    def remove_book(self, isbn: str) -> Optional[Book]:
        for i, book in enumerate(self.books):
            if book.isbn == isbn:
                return self.books.pop(i)
        return None

    def find_by_isbn(self, isbn: str) -> Optional[Book]:
        for book in self.books:
            if book.isbn == isbn:
                return book
        return None

    def find_by_author(self, author: str) -> list:
        return [b for b in self.books if b.author.lower() == author.lower()]
