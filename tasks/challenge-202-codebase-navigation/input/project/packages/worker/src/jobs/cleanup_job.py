"""Database cleanup job handler."""

from ....core.src.logger import get_logger
from ....core.src.database import db

logger = get_logger("cleanup_job")


def handle_cleanup(payload: dict) -> dict:
    """Clean up old records from a table."""
    table = payload.get("table")
    if not table:
        raise ValueError("Table name is required")
    max_age_field = payload.get("age_field", "created_at")
    # In a real system this would filter by age
    count_before = db.count(table)
    logger.info(f"Cleanup job for table '{table}': {count_before} records")
    return {
        "table": table,
        "records_before": count_before,
        "records_removed": 0,
    }


def handle_vacuum(payload: dict) -> dict:
    """Reclaim storage space (no-op for in-memory DB)."""
    logger.info("Vacuum operation completed (no-op for in-memory DB)")
    return {"vacuumed": True}
