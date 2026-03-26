"""Simple route dispatcher."""

import re
from ...core.src.logger import get_logger

logger = get_logger("router")


class Router:
    """Maps (method, path_pattern) to handler functions."""

    def __init__(self):
        self._routes = []

    def add_route(self, method: str, pattern: str, handler, middleware_list=None):
        """Register a route. Pattern uses {param} syntax."""
        regex_pattern = re.sub(r"\{(\w+)\}", r"(?P<\1>[^/]+)", pattern)
        self._routes.append({
            "method": method.upper(),
            "pattern": f"^{regex_pattern}$",
            "handler": handler,
            "middlewares": middleware_list or [],
        })

    def dispatch(self, request: dict) -> dict:
        """Find matching route and invoke handler."""
        method = request["method"].upper()
        path = request["path"]
        for route in self._routes:
            if route["method"] != method:
                continue
            match = re.match(route["pattern"], path)
            if match:
                # Run route-specific middleware
                for mw in route["middlewares"]:
                    result = mw.before(request)
                    if result is not None:
                        return result
                request["params"] = match.groupdict()
                logger.info(f"{method} {path} -> {route['handler'].__name__}")
                return route["handler"](request)
        return {"status": 404, "error": "Not found"}
