"""Job scheduler for recurring tasks."""

import time
from ...core.src.config import get_config
from ...core.src.logger import get_logger
from .queues.job_queue import JobQueue

logger = get_logger("scheduler")


class Scheduler:
    """Schedules recurring jobs at fixed intervals."""

    def __init__(self, queue: JobQueue):
        self.queue = queue
        self._schedules = []

    def add_schedule(self, job_type: str, interval_seconds: int, payload: dict = None):
        """Register a recurring job."""
        self._schedules.append({
            "job_type": job_type,
            "interval": interval_seconds,
            "payload": payload or {},
            "last_run": 0,
        })
        logger.info(f"Scheduled {job_type} every {interval_seconds}s")

    def tick(self) -> int:
        """Check all schedules and enqueue due jobs. Returns count enqueued."""
        now = time.time()
        count = 0
        for schedule in self._schedules:
            if now - schedule["last_run"] >= schedule["interval"]:
                self.queue.enqueue(schedule["job_type"], schedule["payload"])
                schedule["last_run"] = now
                count += 1
        return count

    def get_schedules(self) -> list:
        return [{"type": s["job_type"], "interval": s["interval"]} for s in self._schedules]
