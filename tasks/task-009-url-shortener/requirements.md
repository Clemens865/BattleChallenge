# Task: URL Shortener

## Requirements

Create a Python module `url_shortener.py` that implements a URL shortening service with in-memory and file-based storage.

### `URLShortener` Class

```python
class URLShortener:
    def __init__(self, storage_path: str = None, base_url: str = "https://short.url"):
        """Initialize the shortener.
        - storage_path: optional path to JSON file for persistence. If None, use in-memory only.
        - base_url: base URL prefix for short URLs
        """

    def shorten(self, long_url: str) -> str:
        """Create a short URL for the given long URL.
        - Returns the full short URL (e.g., "https://short.url/abc123")
        - Same long URL always returns the same short URL
        - Short code must be 6-8 alphanumeric characters
        - Must validate that long_url starts with http:// or https://
        - Raises ValueError for invalid URLs
        """

    def resolve(self, short_url: str) -> str:
        """Resolve a short URL back to the original long URL.
        - Accepts either a full short URL or just the code
        - Raises KeyError if the short URL is not found
        """

    def get_stats(self, short_url: str) -> dict:
        """Return usage stats for a short URL.
        - 'long_url': the original URL
        - 'short_url': the short URL
        - 'created_at': ISO format timestamp
        - 'access_count': number of times resolve() was called for this URL
        """

    def list_urls(self) -> list[dict]:
        """Return all stored URL mappings as list of dicts with 'short_url' and 'long_url'."""

    def delete(self, short_url: str) -> None:
        """Delete a short URL mapping. Raises KeyError if not found."""
```

## Acceptance Criteria

- All test cases in `verify/test_outcomes.py` pass
- Short codes are deterministic (same input -> same code)
- No external dependencies (stdlib only)
