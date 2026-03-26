"""Configuration for the book library API."""

DEFAULT_CONFIG = {
    "app_name": "Book Library API",
    "version": "1.0.0",
    "max_results": 100,
    "default_page_size": 20,
    "allowed_genres": [
        "Fiction",
        "Non-Fiction",
        "Science",
        "History",
        "Biography",
        "Technology",
        "General",
    ],
    "date_format": "iso",
}


def get_config(key: str, default=None):
    """Get a configuration value."""
    return DEFAULT_CONFIG.get(key, default)


def get_allowed_genres() -> list:
    return DEFAULT_CONFIG["allowed_genres"]
