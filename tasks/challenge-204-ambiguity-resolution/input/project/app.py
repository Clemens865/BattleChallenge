"""Flask application factory for the blog app."""

from database import Database
from config import get_config


# Global database instance
db = Database()


def create_app(env="development"):
    """Create and configure the Flask application.

    In this simplified version we don't actually use Flask's
    request/response cycle — route handlers are called directly
    with the database instance.  This keeps the demo dependency-free.
    """
    config = get_config(env)
    app_context = {
        "config": config,
        "db": db,
    }
    return app_context


def get_db() -> Database:
    """Return the shared database instance."""
    return db


def reset_db():
    """Reset the database (useful for testing)."""
    global db
    db = Database()
    return db
