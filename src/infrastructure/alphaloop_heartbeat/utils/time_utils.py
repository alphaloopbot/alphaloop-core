"""
Time utilities for AlphaLoop Heartbeat.

This module provides time-related utilities specifically designed for heartbeat
timestamping and time calculations. These utilities ensure consistent time
handling across different timezones and provide accurate timestamp generation.

The utilities handle timezone-aware timestamps, time calculations, and provide
consistent time formatting for heartbeat data.

Key Features:
- Timezone-aware timestamp generation
- Consistent time formatting
- Time difference calculations
- Time validation and parsing
- Cross-platform time handling
"""

from datetime import UTC, datetime
import time


def get_current_timestamp() -> float:
    """
    Get the current timestamp as a Unix timestamp (seconds since epoch).

    Returns the current time as a Unix timestamp, which is the standard
    format for heartbeat timestamps. This function ensures consistent
    time representation across different systems and timezones.

    The timestamp is returned as a float to provide microsecond precision,
    which is important for accurate heartbeat timing and debugging.

    Returns:
        Current Unix timestamp as a float (seconds since epoch)

    Example:
        >>> timestamp = get_current_timestamp()
        >>> print(timestamp)
        1640995200.123456

        >>> # Convert to datetime for human readability
        >>> from datetime import datetime
        >>> dt = datetime.fromtimestamp(timestamp)
        >>> print(dt)
        2022-01-01 00:00:00.123456
    """
    return time.time()


def get_current_datetime() -> datetime:
    """
    Get the current datetime in UTC timezone.

    Returns the current datetime object in UTC timezone, which is the
    standard for heartbeat timestamps. Using UTC ensures consistency
    across different timezones and eliminates timezone-related issues.

    Returns:
        Current datetime object in UTC timezone

    Example:
        >>> dt = get_current_datetime()
        >>> print(dt)
        2022-01-01 00:00:00.123456+00:00

        >>> print(dt.isoformat())
        2022-01-01T00:00:00.123456+00:00
    """
    return datetime.now(UTC)


def format_timestamp(timestamp: float | datetime) -> str:
    """
    Format a timestamp for human-readable output.

    Converts a timestamp (either Unix timestamp or datetime object) into
    a human-readable string format. This function is useful for logging
    and debugging heartbeat timing issues.

    Args:
        timestamp: Unix timestamp (float) or datetime object to format

    Returns:
        Formatted timestamp string in ISO format

    Example:
        >>> timestamp = get_current_timestamp()
        >>> formatted = format_timestamp(timestamp)
        >>> print(formatted)
        2022-01-01T00:00:00.123456+00:00

        >>> dt = get_current_datetime()
        >>> formatted = format_timestamp(dt)
        >>> print(formatted)
        2022-01-01T00:00:00.123456+00:00
    """
    if isinstance(timestamp, int | float):
        dt = datetime.fromtimestamp(timestamp, tz=UTC)
    else:
        dt = timestamp

    return dt.isoformat()


def calculate_time_difference(timestamp1: float | datetime, timestamp2: float | datetime) -> float:
    """
    Calculate the time difference between two timestamps.

    Calculates the absolute time difference between two timestamps in seconds.
    This function is useful for determining how old a heartbeat is or
    calculating intervals between heartbeat generations.

    Args:
        timestamp1: First timestamp (Unix timestamp or datetime)
        timestamp2: Second timestamp (Unix timestamp or datetime)

    Returns:
        Time difference in seconds (always positive)

    Example:
        >>> start_time = get_current_timestamp()
        >>> time.sleep(1.5)
        >>> end_time = get_current_timestamp()
        >>> diff = calculate_time_difference(start_time, end_time)
        >>> print(f"Time difference: {diff:.2f} seconds")
        Time difference: 1.50 seconds
    """
    # Convert to Unix timestamps if needed
    if isinstance(timestamp1, datetime):
        ts1 = timestamp1.timestamp()
    else:
        ts1 = float(timestamp1)

    if isinstance(timestamp2, datetime):
        ts2 = timestamp2.timestamp()
    else:
        ts2 = float(timestamp2)

    return abs(ts2 - ts1)


def is_timestamp_recent(timestamp: float | datetime, max_age_seconds: float) -> bool:
    """
    Check if a timestamp is recent (within the specified age limit).

    Determines whether a timestamp is recent enough based on the specified
    maximum age threshold. This function is commonly used in heartbeat
    checking to determine if a service is still healthy.

    Args:
        timestamp: Timestamp to check (Unix timestamp or datetime)
        max_age_seconds: Maximum age in seconds to consider as "recent"

    Returns:
        True if the timestamp is within the age limit, False otherwise

    Example:
        >>> heartbeat_time = get_current_timestamp()
        >>> time.sleep(30)
        >>> is_recent = is_timestamp_recent(heartbeat_time, 60)
        >>> print(f"Heartbeat is recent: {is_recent}")
        Heartbeat is recent: True

        >>> is_recent = is_timestamp_recent(heartbeat_time, 10)
        >>> print(f"Heartbeat is recent: {is_recent}")
        Heartbeat is recent: False
    """
    current_time = get_current_timestamp()

    if isinstance(timestamp, datetime):
        check_time = timestamp.timestamp()
    else:
        check_time = float(timestamp)

    age = current_time - check_time
    return age <= max_age_seconds


def parse_timestamp(timestamp_str: str) -> datetime | None:
    """
    Parse a timestamp string into a datetime object.

    Attempts to parse various timestamp string formats into a datetime object.
    This function is useful for reading timestamps from configuration files
    or external sources and converting them to datetime objects for processing.

    Supported formats:
    - ISO format: "2022-01-01T00:00:00.123456+00:00"
    - Unix timestamp: "1640995200.123456"
    - Simple datetime: "2022-01-01 00:00:00"

    Args:
        timestamp_str: String representation of timestamp

    Returns:
        Parsed datetime object or None if parsing fails

    Example:
        >>> dt = parse_timestamp("2022-01-01T00:00:00.123456+00:00")
        >>> print(dt)
        2022-01-01 00:00:00.123456+00:00

        >>> dt = parse_timestamp("1640995200.123456")
        >>> print(dt)
        2022-01-01 00:00:00.123456+00:00

        >>> dt = parse_timestamp("invalid")
        >>> print(dt)
        None
    """
    try:
        # Try ISO format first
        return datetime.fromisoformat(timestamp_str)
    except ValueError:
        try:
            # Try Unix timestamp
            timestamp_float = float(timestamp_str)
            return datetime.fromtimestamp(timestamp_float, tz=UTC)
        except ValueError:
            try:
                # Try simple datetime format
                return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
            except ValueError:
                return None


def get_timestamp_age(timestamp: float | datetime) -> float:
    """
    Calculate the age of a timestamp in seconds.

    Calculates how old a timestamp is by comparing it to the current time.
    This function is useful for determining the age of heartbeat data
    and for cleanup operations.

    Args:
        timestamp: Timestamp to calculate age for (Unix timestamp or datetime)

    Returns:
        Age of the timestamp in seconds

    Example:
        >>> heartbeat_time = get_current_timestamp()
        >>> time.sleep(5)
        >>> age = get_timestamp_age(heartbeat_time)
        >>> print(f"Heartbeat age: {age:.2f} seconds")
        Heartbeat age: 5.00 seconds
    """
    current_time = get_current_timestamp()

    if isinstance(timestamp, datetime):
        check_time = timestamp.timestamp()
    else:
        check_time = float(timestamp)

    return current_time - check_time


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds into a human-readable string.

    Converts a duration in seconds into a human-readable format showing
    days, hours, minutes, and seconds as appropriate. This function is
    useful for logging and displaying heartbeat ages and intervals.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string

    Example:
        >>> duration = format_duration(3661.5)
        >>> print(duration)
        1h 1m 1s

        >>> duration = format_duration(86400)
        >>> print(duration)
        1d 0h 0m 0s

        >>> duration = format_duration(30.5)
        >>> print(duration)
        30s
    """
    if seconds < 0:
        return "0s"

    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0 or days > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or hours > 0 or days > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")

    return " ".join(parts)
