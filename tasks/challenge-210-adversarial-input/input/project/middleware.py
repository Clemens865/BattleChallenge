"""Middleware for request processing."""
import time
from functools import wraps


# Simple in-memory rate limiter
_rate_limit_store = {}


def rate_limit(max_requests: int = 5, window_seconds: int = 60):
    """Rate limiting decorator."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client_ip = kwargs.get("client_ip", "unknown")
            now = time.time()

            if client_ip not in _rate_limit_store:
                _rate_limit_store[client_ip] = []

            # Clean old entries
            _rate_limit_store[client_ip] = [
                t for t in _rate_limit_store[client_ip]
                if now - t < window_seconds
            ]

            if len(_rate_limit_store[client_ip]) >= max_requests:
                return {"error": "Rate limit exceeded", "status": 429}

            _rate_limit_store[client_ip].append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_auth(func):
    """Authentication required decorator."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = kwargs.get("auth_token")
        if not token:
            return {"error": "Authentication required", "status": 401}
        # Token validation would go here
        return func(*args, **kwargs)
    return wrapper
