"""Shared exception classes."""


class AppError(Exception):
    """Base application error."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(AppError):
    def __init__(self, resource: str, identifier: str = ""):
        msg = f"{resource} not found"
        if identifier:
            msg += f": {identifier}"
        super().__init__(msg, status_code=404)


class ValidationError(AppError):
    def __init__(self, errors: list):
        super().__init__("Validation failed", status_code=400)
        self.errors = errors


class AuthenticationError(AppError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status_code=401)


class AuthorizationError(AppError):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=403)
