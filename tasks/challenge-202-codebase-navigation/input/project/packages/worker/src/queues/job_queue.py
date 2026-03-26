"""In-memory job queue."""

from collections import deque
from ....core.src.helpers import generate_id, timestamp_iso
from ....core.src.logger import get_logger

logger = get_logger("job_queue")


class JobQueue:
    """Simple FIFO job queue backed by a deque."""

    def __init__(self):
        self._pending = deque()
        self._completed = {}
        self._failed = {}

    def enqueue(self, job_type: str, payload: dict = None) -> str:
        """Add a job to the queue. Returns the job ID."""
        job_id = generate_id()
        job = {
            "id": job_id,
            "type": job_type,
            "payload": payload or {},
            "status": "pending",
            "created_at": timestamp_iso(),
        }
        self._pending.append(job)
        logger.info(f"Enqueued job {job_id} ({job_type})")
        return job_id

    def dequeue(self):
        """Get the next pending job, or None."""
        if not self._pending:
            return None
        return self._pending.popleft()

    def complete(self, job_id: str, result=None) -> None:
        self._completed[job_id] = {"result": result, "completed_at": timestamp_iso()}

    def fail(self, job_id: str, error: str) -> None:
        self._failed[job_id] = {"error": error, "failed_at": timestamp_iso()}

    def pending_count(self) -> int:
        return len(self._pending)

    def stats(self) -> dict:
        return {
            "pending": len(self._pending),
            "completed": len(self._completed),
            "failed": len(self._failed),
        }
