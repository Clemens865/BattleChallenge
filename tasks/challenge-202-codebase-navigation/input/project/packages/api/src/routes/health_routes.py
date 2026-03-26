"""Health check routes."""

from ....core.src.config import get_config
from ....core.src.database import db


def register(router):
    """Register health check routes."""
    router.add_route("GET", "/api/health", health_check)
    router.add_route("GET", "/api/health/ready", readiness_check)


def health_check(request: dict) -> dict:
    """GET /api/health — basic liveness check."""
    return {
        "status": 200,
        "data": {
            "status": "healthy",
            "app": get_config("APP_NAME"),
            "version": get_config("APP_VERSION"),
        },
    }


def readiness_check(request: dict) -> dict:
    """GET /api/health/ready — checks dependencies are available."""
    checks = {
        "database": True,  # In-memory DB is always ready
        "config": get_config("APP_NAME") is not None,
    }
    all_ready = all(checks.values())
    return {
        "status": 200 if all_ready else 503,
        "data": {"ready": all_ready, "checks": checks},
    }
