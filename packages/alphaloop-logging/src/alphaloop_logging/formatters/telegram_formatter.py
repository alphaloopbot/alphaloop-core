"""Telegram logging formatter with HTML support."""

from datetime import datetime
from typing import Any

from .base import BaseFormatter


class TelegramFormatter(BaseFormatter):
    """Formatter for Telegram logging with HTML formatting."""

    # Emoji and style mapping for log levels
    LEVEL_STYLES = {
        "DEBUG": {"emoji": "🔍", "style": "🚧 DEBUG 🚧"},
        "INFO": {"emoji": "📢", "style": "📢 INFO 📢"},
        "WARNING": {"emoji": "⚠️", "style": "⚠️ WARNING ⚠️"},
        "ERROR": {"emoji": "🚨", "style": "🚨 ERROR 🚨"},
        "CRITICAL": {"emoji": "💥", "style": "🚨 CRITICAL 🚨"},
    }

    def __init__(
        self,
        hostname: str = "unknown",
        include_file_info: bool = True,
        max_message_length: int = 3000,
    ) -> None:
        """
        Initialize Telegram formatter.

        Args:
            hostname: Hostname to include in messages.
            include_file_info: Whether to include file information.
            max_message_length: Maximum message length.
        """
        self.hostname = hostname.capitalize()
        self.include_file_info = include_file_info
        self.max_message_length = max_message_length

    def format(self, record: dict[str, Any]) -> str:
        """
        Format log record for Telegram with HTML formatting.

        Args:
            record: The log record dictionary.

        Returns:
            HTML-formatted message for Telegram.
        """
        timestamp = record.get("timestamp", datetime.now())
        if isinstance(timestamp, datetime):
            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp_str = str(timestamp)

        level = record.get("level", "INFO").upper()
        message = record.get("message", "")
        app_name = record.get("app_name", "")
        info = record.get("info", "")
        file_name = record.get("file_name", "")

        # Truncate message if too long
        if len(message) > self.max_message_length:
            message = f"{message[:self.max_message_length]}..."

        # Get level style
        level_info = self.LEVEL_STYLES.get(level, self.LEVEL_STYLES["INFO"])
        level_style = level_info["style"]

        # Build HTML message
        html_parts = [
            f"<b>{level_style}</b>",
            f"💻 <b>{self.hostname}</b>",
            f"⏰ <i><b>{timestamp_str} (UTC)</b></i>",
        ]

        if file_name and self.include_file_info:
            html_parts.append(f"📂 <b>Log File:</b>\n<i>{file_name}</i>")

        if app_name:
            html_parts.append(f"🏷️ <b>App:</b>\n<i>{app_name}</i>")

        if info:
            html_parts.append(f"⚙️ <b>Context:</b>\n<i>{info}</i>")

        html_parts.append(f"📄 <b>Message:</b>\n{self._escape_html(message)}")

        return "\n\n".join(html_parts)

    def _escape_html(self, text: str) -> str:
        """
        Escape HTML special characters.

        Args:
            text: Text to escape.

        Returns:
            HTML-escaped text.
        """
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
        )
