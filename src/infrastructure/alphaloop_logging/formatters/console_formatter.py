"""Console logging formatter with color support."""

from datetime import datetime
from typing import Any

from rich.console import Console
from rich.text import Text

from .base import BaseFormatter


class ConsoleFormatter(BaseFormatter):
    """Formatter for console logging with color support."""

    # Color mapping for log levels
    LEVEL_COLORS = {
        "DEBUG": "dim white",
        "INFO": "blue",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold red on white",
    }

    # Emoji mapping for log levels
    LEVEL_EMOJIS = {
        "DEBUG": "🔍",
        "INFO": "📢",
        "WARNING": "⚠️",
        "ERROR": "🚨",
        "CRITICAL": "💥",
    }

    def __init__(
        self,
        use_colors: bool = True,
        show_timestamp: bool = True,
        show_level: bool = True,
        include_caller_info: bool = True,
    ) -> None:
        """
        Initialize console formatter.

        Args:
            use_colors: Whether to use colors in output.
            show_timestamp: Whether to show timestamp.
            show_level: Whether to show log level.
            include_caller_info: Whether to include caller information.
        """
        self.use_colors = use_colors
        self.show_timestamp = show_timestamp
        self.show_level = show_level
        self.include_caller_info = include_caller_info
        self.console = Console() if use_colors else None

    def format(self, record: dict[str, Any]) -> str:
        """
        Format log record for console output.

        Args:
            record: The log record dictionary.

        Returns:
            Formatted log message string.
        """
        timestamp = record.get("timestamp", datetime.now())
        if isinstance(timestamp, datetime):
            timestamp_str = timestamp.strftime("%H:%M:%S")
        else:
            timestamp_str = str(timestamp)

        level = record.get("level", "INFO").upper()
        message = record.get("message", "")
        app_name = record.get("app_name", "")
        info = record.get("info", "")

        # Build the formatted message
        parts = []

        if self.show_timestamp:
            parts.append(f"[{timestamp_str}]")

        if self.show_level:
            emoji = self.LEVEL_EMOJIS.get(level, "📝")
            parts.append(f"{emoji} {level}")

        if app_name:
            parts.append(f"[{app_name}]")

        if info and self.include_caller_info:
            parts.append(f"({info})")

        parts.append("->")
        parts.append(message)

        formatted_message = " ".join(parts)

        # Apply colors if enabled
        if self.use_colors and self.console:
            color = self.LEVEL_COLORS.get(level, "white")
            text = Text(formatted_message, style=color)
            return str(text)

        # Truncate if necessary
        return self.truncate_message(formatted_message)
