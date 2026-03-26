"""In-memory database for the book library."""

from .models import Book, BookCollection


class Database:
    """Simple in-memory database backed by BookCollection."""

    def __init__(self):
        self._collection = BookCollection(name="main")

    def insert(self, book: Book) -> Book:
        self._collection.add_book(book)
        return book

    def get_all(self) -> list:
        return list(self._collection.books)

    def get_by_id(self, book_id: str):
        for book in self._collection.books:
            if book.id == book_id:
                return book
        return None

    def get_by_isbn(self, isbn: str):
        return self._collection.find_by_isbn(isbn)

    def delete(self, book_id: str) -> bool:
        for i, book in enumerate(self._collection.books):
            if book.id == book_id:
                self._collection.books.pop(i)
                return True
        return False

    def count(self) -> int:
        return len(self._collection.books)

    def clear(self) -> None:
        self._collection.books.clear()
