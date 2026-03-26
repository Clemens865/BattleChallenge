"""Middleware for request/response processing."""

import time
from .config import get_config


class RequestLogger:
    """Logs API requests with timing information."""

    def __init__(self):
        self.logs = []

    def before_request(self, method: str, path: str) -> dict:
        entry = {
            "method": method,
            "path": path,
            "start_time": time.time(),
        }
        return entry

    def after_request(self, entry: dict, response: dict) -> None:
        entry["end_time"] = time.time()
        entry["duration_ms"] = (entry["end_time"] - entry["start_time"]) * 1000
        entry["status"] = response.get("status", 0)
        self.logs.append(entry)

    def get_logs(self) -> list:
        return list(self.logs)

    def clear_logs(self) -> None:
        self.logs.clear()


class ResponseFormatter:
    """Ensures consistent response format."""

    @staticmethod
    def format(response: dict) -> dict:
        app_name = get_config("app_name", "API")
        formatted = {
            "api": app_name,
            "status": response.get("status", 500),
        }
        if "data" in response:
            formatted["data"] = response["data"]
        if "error" in response:
            formatted["error"] = response["error"]
        if "errors" in response:
            formatted["errors"] = response["errors"]
        if "count" in response:
            formatted["count"] = response["count"]
        return formatted
