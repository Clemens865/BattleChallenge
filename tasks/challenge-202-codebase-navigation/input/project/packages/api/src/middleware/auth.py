"""Authentication middleware.

This is the canonical middleware pattern in this codebase.
New middleware should follow this same structure.
"""

from ....core.src.config import get_config
from ....core.src.logger import get_logger
from ....core.src.crypto import verify_password

logger = get_logger("auth_middleware")

# Paths that do not require authentication
PUBLIC_PATHS = [
    "/api/health",
    "/api/health/ready",
]


class AuthMiddleware:
    """Checks for valid auth token on non-public paths."""

    def __init__(self):
        self.enabled = get_config("AUTH_ENABLED", True)
        self.token_header = "Authorization"
        logger.info("AuthMiddleware initialized (enabled=%s)", self.enabled)

    def before(self, request: dict):
        """Check authentication before request processing.

        Returns None to continue, or a response dict to short-circuit.
        """
        if not self.enabled:
            return None
        path = request.get("path", "")
        if path in PUBLIC_PATHS:
            return None
        headers = request.get("headers", {})
        token = headers.get(self.token_header)
        if not token:
            return {"status": 401, "error": "Authentication required"}
        # In production this would verify a JWT; here we accept any non-empty token
        if token == "invalid":
            return {"status": 401, "error": "Invalid token"}
        request["user_id"] = "authenticated-user"
        return None

    def after(self, request: dict, response: dict) -> dict:
        """No post-processing needed for auth."""
        return response
