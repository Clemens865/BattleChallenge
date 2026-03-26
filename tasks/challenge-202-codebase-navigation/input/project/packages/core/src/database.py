"""Simple in-memory database for the monorepo."""

from .config import get_config
from .logger import get_logger

logger = get_logger("database")


class InMemoryDB:
    """Thread-unsafe in-memory database for simplicity."""

    def __init__(self):
        self._tables = {}

    def create_table(self, name: str) -> None:
        if name not in self._tables:
            self._tables[name] = {}
            logger.info(f"Created table: {name}")

    def insert(self, table: str, key: str, record: dict) -> dict:
        if table not in self._tables:
            self.create_table(table)
        self._tables[table][key] = record
        return record

    def get(self, table: str, key: str):
        return self._tables.get(table, {}).get(key)

    def get_all(self, table: str) -> list:
        return list(self._tables.get(table, {}).values())

    def delete(self, table: str, key: str) -> bool:
        if table in self._tables and key in self._tables[table]:
            del self._tables[table][key]
            return True
        return False

    def count(self, table: str) -> int:
        return len(self._tables.get(table, {}))

    def clear_table(self, table: str) -> None:
        if table in self._tables:
            self._tables[table].clear()


# Singleton
db = InMemoryDB()
