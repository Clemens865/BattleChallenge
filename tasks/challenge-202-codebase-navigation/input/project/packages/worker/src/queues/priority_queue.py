"""Priority-based job queue."""

import heapq
from ....core.src.helpers import generate_id, timestamp_iso


class PriorityJobQueue:
    """Job queue that processes higher-priority jobs first."""

    def __init__(self):
        self._heap = []
        self._counter = 0

    def enqueue(self, job_type: str, payload: dict = None, priority: int = 5) -> str:
        """Add a job. Lower priority number = higher priority."""
        job_id = generate_id()
        self._counter += 1
        job = {
            "id": job_id,
            "type": job_type,
            "payload": payload or {},
            "priority": priority,
            "created_at": timestamp_iso(),
        }
        heapq.heappush(self._heap, (priority, self._counter, job))
        return job_id

    def dequeue(self):
        """Get the highest-priority pending job."""
        if not self._heap:
            return None
        _, _, job = heapq.heappop(self._heap)
        return job

    def pending_count(self) -> int:
        return len(self._heap)
