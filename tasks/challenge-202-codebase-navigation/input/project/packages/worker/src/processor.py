"""Main job processor that runs background tasks."""

import time
from ...core.src.config import get_config
from ...core.src.logger import get_logger
from ...core.src.base import BaseService
from .queues.job_queue import JobQueue

logger = get_logger("processor")


class JobProcessor(BaseService):
    """Processes jobs from the queue."""

    def __init__(self):
        super().__init__("JobProcessor")
        self.queue = JobQueue()
        self.concurrency = get_config("WORKER_CONCURRENCY", 4)
        self.poll_interval = get_config("WORKER_POLL_INTERVAL", 5)
        self.running = False
        self._handlers = {}

    def register_handler(self, job_type: str, handler) -> None:
        """Register a handler function for a job type."""
        self._handlers[job_type] = handler
        self.log_info(f"Registered handler for: {job_type}")

    def process_one(self) -> bool:
        """Process a single job from the queue. Returns True if a job was processed."""
        job = self.queue.dequeue()
        if job is None:
            return False
        job_type = job.get("type", "unknown")
        handler = self._handlers.get(job_type)
        if handler is None:
            self.log_error(f"No handler for job type: {job_type}")
            self.queue.fail(job["id"], "No handler registered")
            return True
        try:
            result = handler(job.get("payload", {}))
            self.queue.complete(job["id"], result)
            self.log_info(f"Completed job {job['id']} ({job_type})")
        except Exception as e:
            self.queue.fail(job["id"], str(e))
            self.log_error(f"Failed job {job['id']}: {e}")
        return True

    def process_all(self) -> int:
        """Process all pending jobs. Returns count of jobs processed."""
        count = 0
        while self.process_one():
            count += 1
        return count
