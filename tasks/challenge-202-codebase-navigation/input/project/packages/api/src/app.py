"""Main application class that wires routes and middleware."""

from ...core.src.config import get_config
from ...core.src.logger import get_logger
from .router import Router
from .middleware.auth import AuthMiddleware
from .middleware.cors import CorsMiddleware
from .middleware.logging_mw import LoggingMiddleware
from .routes import user_routes, health_routes, team_routes

logger = get_logger("app")


class Application:
    """The main API application."""

    def __init__(self):
        self.router = Router()
        self.middlewares = []
        self._setup_middleware()
        self._setup_routes()

    def _setup_middleware(self):
        self.middlewares.append(LoggingMiddleware())
        self.middlewares.append(CorsMiddleware())
        if get_config("AUTH_ENABLED", True):
            self.middlewares.append(AuthMiddleware())

    def _setup_routes(self):
        user_routes.register(self.router)
        health_routes.register(self.router)
        team_routes.register(self.router)

    def handle_request(self, method: str, path: str, body: dict = None,
                       headers: dict = None, client_ip: str = "127.0.0.1") -> dict:
        """Process a request through middleware chain then router."""
        request = {
            "method": method,
            "path": path,
            "body": body or {},
            "headers": headers or {},
            "client_ip": client_ip,
        }
        # Run before-middleware
        for mw in self.middlewares:
            result = mw.before(request)
            if result is not None:
                return result
        # Dispatch to route handler
        response = self.router.dispatch(request)
        # Run after-middleware
        for mw in reversed(self.middlewares):
            response = mw.after(request, response)
        return response
