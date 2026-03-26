"""Central configuration system used across all packages.

All config keys have defaults. Packages should use get_config() to read
values and set_config() to override them in tests.
"""

_DEFAULTS = {
    "APP_NAME": "MonoRepo API",
    "APP_VERSION": "2.1.0",
    "DEBUG": False,
    "LOG_LEVEL": "INFO",
    "DATABASE_URL": "sqlite:///data.db",
    "SECRET_KEY": "change-me-in-production",
    "TOKEN_EXPIRY_SECONDS": 3600,
    "MAX_PAGE_SIZE": 100,
    "DEFAULT_PAGE_SIZE": 20,
    "WORKER_CONCURRENCY": 4,
    "WORKER_POLL_INTERVAL": 5,
    "JOB_TIMEOUT_SECONDS": 300,
    "CORS_ORIGINS": "*",
    "AUTH_ENABLED": True,
}

_overrides = {}


def get_config(key: str, default=None):
    """Get a configuration value. Checks overrides first, then defaults."""
    if key in _overrides:
        return _overrides[key]
    if key in _DEFAULTS:
        return _DEFAULTS[key]
    return default


def set_config(key: str, value) -> None:
    """Override a configuration value (useful for testing)."""
    _overrides[key] = value


def reset_config() -> None:
    """Clear all overrides, restoring defaults."""
    _overrides.clear()


def get_all_config() -> dict:
    """Return merged config (defaults + overrides)."""
    merged = dict(_DEFAULTS)
    merged.update(_overrides)
    return merged
