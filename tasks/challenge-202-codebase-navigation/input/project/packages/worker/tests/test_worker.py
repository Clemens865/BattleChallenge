"""Tests for worker job processing."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from packages.worker.src.queues.job_queue import JobQueue
from packages.worker.src.processor import JobProcessor


def test_enqueue_and_dequeue():
    q = JobQueue()
    job_id = q.enqueue("test_job", {"key": "value"})
    assert q.pending_count() == 1
    job = q.dequeue()
    assert job["id"] == job_id
    assert job["type"] == "test_job"


def test_process_job():
    processor = JobProcessor()
    results = []
    processor.register_handler("echo", lambda p: results.append(p))
    processor.queue.enqueue("echo", {"msg": "hello"})
    count = processor.process_all()
    assert count == 1
    assert results[0] == {"msg": "hello"}


def test_queue_stats():
    q = JobQueue()
    q.enqueue("a")
    q.enqueue("b")
    stats = q.stats()
    assert stats["pending"] == 2
    assert stats["completed"] == 0
