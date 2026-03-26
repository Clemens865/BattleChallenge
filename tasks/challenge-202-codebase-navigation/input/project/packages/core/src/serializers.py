"""Shared serialization utilities."""

from datetime import datetime, date


def serialize_datetime(value) -> str:
    """Convert datetime/date to ISO string."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def serialize_record(record: dict, fields: list = None) -> dict:
    """Serialize a database record, optionally filtering to specific fields."""
    if fields is None:
        return dict(record)
    return {k: record[k] for k in fields if k in record}


def paginate(items: list, page: int = 1, page_size: int = 20) -> dict:
    """Paginate a list of items."""
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": items[start:end],
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size,
    }
