"""Logging utilities shared across packages."""

import logging
import sys
from .config import get_config


_loggers = {}


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with the configured log level."""
    if name in _loggers:
        return _loggers[name]
    logger = logging.getLogger(name)
    level = get_config("LOG_LEVEL", "INFO")
    logger.setLevel(getattr(logging, level, logging.INFO))
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        fmt = logging.Formatter("[%(asctime)s] %(name)s %(levelname)s: %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    _loggers[name] = logger
    return logger
