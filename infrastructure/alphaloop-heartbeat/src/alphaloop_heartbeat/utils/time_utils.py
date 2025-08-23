"""Time utilities for heartbeat management."""

from datetime import UTC, datetime


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(UTC).isoformat()


def get_current_datetime() -> datetime:
    """Get current datetime with timezone."""
    return datetime.now(UTC)


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse timestamp string to datetime."""
    return datetime.fromisoformat(timestamp_str)


def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO timestamp string."""
    return dt.isoformat()


def is_timestamp_recent(timestamp_str: str, max_age_seconds: int) -> bool:
    """Check if a timestamp is recent (within max_age_seconds)."""
    try:
        timestamp = parse_timestamp(timestamp_str)
        current_time = get_current_datetime()
        age = (current_time - timestamp).total_seconds()
        return age <= max_age_seconds
    except Exception:
        return False
