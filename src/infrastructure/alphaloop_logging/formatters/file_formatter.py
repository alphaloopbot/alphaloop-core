"""File logging formatter."""

from datetime import datetime
from typing import Any

from .base import BaseFormatter


class FileFormatter(BaseFormatter):
    """Formatter for file logging."""

    def __init__(self, include_caller_info: bool = True) -> None:
        """
        Initialize file formatter.

        Args:
            include_caller_info: Whether to include caller information.
        """
        self.include_caller_info = include_caller_info

    def format(self, record: dict[str, Any]) -> str:
        """
        Format log record for file output.

        Args:
            record: The log record dictionary.

        Returns:
            Formatted log message string.
        """
        timestamp = record.get("timestamp", datetime.now())
        if isinstance(timestamp, datetime):
            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp_str = str(timestamp)

        level = record.get("level", "INFO")
        message = record.get("message", "")
        app_name = record.get("app_name", "")
        info = record.get("info", "")

        # Build the log line
        parts = [timestamp_str, "->", level.upper()]

        if app_name:
            parts.append(f"[{app_name}]")

        if info and self.include_caller_info:
            parts.append(f"({info})")

        parts.append(message)

        formatted_message = " ".join(parts)

        # Truncate if necessary
        return self.truncate_message(formatted_message)
