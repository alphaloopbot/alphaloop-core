"""Base handler interface."""

from abc import ABC, abstractmethod
from typing import Any

from ..formatters.base import BaseFormatter


class BaseHandler(ABC):
    """Abstract base class for log handlers."""

    def __init__(self, formatter: BaseFormatter | None = None) -> None:
        """
        Initialize handler.

        Args:
            formatter: The formatter to use for this handler.
        """
        self.formatter = formatter

    @abstractmethod
    async def emit(self, record: dict[str, Any]) -> None:
        """
        Emit a log record.

        Args:
            record: The log record dictionary.
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the handler and clean up resources."""
        pass

    def should_handle(self, record: dict[str, Any]) -> bool:
        """
        Determine if this handler should handle the given record.

        Args:
            record: The log record dictionary.

        Returns:
            True if this handler should process the record.
        """
        _ = record  # Mark as used
        return True  # Default: handle all records

    def format_record(self, record: dict[str, Any]) -> str:
        """
        Format a log record using the configured formatter.

        Args:
            record: The log record dictionary.

        Returns:
            Formatted message string.
        """
        if self.formatter:
            return self.formatter.format(record)
        return str(record.get("message", ""))
