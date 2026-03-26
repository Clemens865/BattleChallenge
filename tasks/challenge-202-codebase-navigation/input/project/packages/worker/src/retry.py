"""Retry logic for failed jobs."""

import time
from ...core.src.config import get_config
from ...core.src.logger import get_logger

logger = get_logger("retry")


class RetryPolicy:
    """Configurable retry policy with exponential backoff."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def should_retry(self, attempt: int) -> bool:
        return attempt < self.max_retries

    def get_delay(self, attempt: int) -> float:
        delay = self.base_delay * (2 ** attempt)
        return min(delay, self.max_delay)

    def execute_with_retry(self, func, *args, **kwargs):
        """Execute a function with retry logic."""
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if not self.should_retry(attempt + 1):
                    break
                delay = self.get_delay(attempt)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay:.1f}s: {e}")
                time.sleep(delay)
        raise last_error
