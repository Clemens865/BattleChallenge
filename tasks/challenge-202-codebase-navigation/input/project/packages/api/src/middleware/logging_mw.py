"""Request logging middleware."""

import time
from ....core.src.logger import get_logger

logger = get_logger("request_logger")


class LoggingMiddleware:
    """Logs request method, path, and response time."""

    def __init__(self):
        self.logs = []

    def before(self, request: dict):
        """Record request start time."""
        request["_start_time"] = time.time()
        return None

    def after(self, request: dict, response: dict) -> dict:
        """Log the completed request."""
        start = request.pop("_start_time", None)
        duration = (time.time() - start) * 1000 if start else 0
        entry = {
            "method": request.get("method"),
            "path": request.get("path"),
            "status": response.get("status"),
            "duration_ms": round(duration, 2),
        }
        self.logs.append(entry)
        logger.info(
            "%s %s -> %s (%.1fms)",
            entry["method"], entry["path"], entry["status"], entry["duration_ms"],
        )
        return response

    def get_logs(self) -> list:
        return list(self.logs)
