"""CORS middleware — adds cross-origin headers to responses."""

from ....core.src.config import get_config
from ....core.src.logger import get_logger

logger = get_logger("cors_middleware")


class CorsMiddleware:
    """Adds CORS headers to every response."""

    def __init__(self):
        self.allowed_origins = get_config("CORS_ORIGINS", "*")

    def before(self, request: dict):
        """Handle preflight OPTIONS requests."""
        if request.get("method", "").upper() == "OPTIONS":
            return {
                "status": 204,
                "headers": self._cors_headers(),
            }
        return None

    def after(self, request: dict, response: dict) -> dict:
        """Add CORS headers to the response."""
        if "headers" not in response:
            response["headers"] = {}
        response["headers"].update(self._cors_headers())
        return response

    def _cors_headers(self) -> dict:
        return {
            "Access-Control-Allow-Origin": self.allowed_origins,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
