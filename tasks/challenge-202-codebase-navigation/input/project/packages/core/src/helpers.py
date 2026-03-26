"""Miscellaneous helper functions."""

import uuid
import time


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def timestamp() -> float:
    """Current UTC timestamp."""
    return time.time()


def timestamp_iso() -> str:
    """Current UTC time as ISO string."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def chunk_list(lst: list, size: int) -> list:
    """Split a list into chunks of given size."""
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def safe_get(data: dict, *keys, default=None):
    """Safely traverse nested dicts."""
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return current
