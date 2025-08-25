"""Base formatter interface."""

from abc import ABC, abstractmethod
from typing import Any


class BaseFormatter(ABC):
    """Abstract base class for log formatters."""

    @abstractmethod
    def format(self, record: dict[str, Any]) -> str:
        """
        Format a log record.

        Args:
            record: The log record dictionary.

        Returns:
            Formatted log message string.
        """
        pass

    def truncate_message(self, message: str, max_length: int = 3000) -> str:
        """
        Truncate message if it's too long.

        Args:
            message: The message to truncate.
            max_length: Maximum allowed length.

        Returns:
            Truncated message if necessary.
        """
        if max_length <= 0:
            return ""
        if len(message) <= max_length:
            return message
        # Use a single character ellipsis to stay within max_length
        return f"{message[:max_length-1]}…"
