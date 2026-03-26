"""Base classes for services across packages."""

from .config import get_config
from .logger import get_logger


class BaseService:
    """Base class that all services inherit from."""

    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.logger = get_logger(self.name)
        self.debug = get_config("DEBUG", False)

    def log_info(self, message: str) -> None:
        self.logger.info(f"[{self.name}] {message}")

    def log_error(self, message: str) -> None:
        self.logger.error(f"[{self.name}] {message}")

    def log_debug(self, message: str) -> None:
        if self.debug:
            self.logger.debug(f"[{self.name}] {message}")
