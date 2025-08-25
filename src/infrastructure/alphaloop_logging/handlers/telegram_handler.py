"""Telegram logging handler."""

import asyncio
from typing import Any

import aiohttp

from ..config.settings import LogLevel, TelegramConfig
from ..exceptions import TelegramError
from ..formatters.telegram_formatter import TelegramFormatter
from .base import BaseHandler


class TelegramHandler(BaseHandler):
    """Handler for sending logs to Telegram."""

    def __init__(self, config: TelegramConfig, hostname: str = "unknown") -> None:
        """
        Initialize Telegram handler.

        Args:
            config: Telegram configuration.
            hostname: Hostname to include in messages.
        """
        formatter = TelegramFormatter(
            hostname=hostname, max_message_length=config.max_message_length
        )
        super().__init__(formatter)
        self.config = config
        self._session: aiohttp.ClientSession | None = None
        self._rate_limit_delay = 1.0  # Seconds between messages
        self._last_send_time = 0.0

    def should_handle(self, record: dict[str, Any]) -> bool:
        """
        Determine if this handler should handle the given record.

        Args:
            record: The log record dictionary.

        Returns:
            True if this handler should process the record.
        """
        if not self.config.enabled:
            return False

        level = record.get("level", "INFO").upper()
        telegram_override = record.get("telegram")

        # Check explicit telegram override
        if telegram_override is True:
            return True
        elif telegram_override is False:
            return False

        # Check level-based configuration
        level_config_map = {
            LogLevel.DEBUG: self.config.send_on_debug,
            LogLevel.INFO: self.config.send_on_info,
            LogLevel.WARNING: self.config.send_on_warning,
            LogLevel.ERROR: self.config.send_on_error,
            LogLevel.CRITICAL: self.config.send_on_critical,
        }

        try:
            log_level = LogLevel(level)
            return level_config_map.get(log_level, False)
        except ValueError:
            return False

    async def emit(self, record: dict[str, Any]) -> None:
        """
        Send log record to Telegram.

        Args:
            record: The log record dictionary.
        """
        if not self.should_handle(record):
            return

        try:
            # Rate limiting
            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - self._last_send_time
            if time_since_last < self._rate_limit_delay:
                await asyncio.sleep(self._rate_limit_delay - time_since_last)

            # Format message
            formatted_message = self.format_record(record)

            # Send to Telegram
            await self._send_message(formatted_message)
            self._last_send_time = asyncio.get_event_loop().time()

        except Exception as e:
            # Don't raise exceptions from telegram handler to avoid recursion
            # Just print error to stderr
            import sys

            print(f"Telegram handler error: {e}", file=sys.stderr)

    async def _send_message(self, message: str) -> None:
        """
        Send message to Telegram.

        Args:
            message: The message to send.
        """
        if not self._session:
            self._session = aiohttp.ClientSession()

        url = f"https://api.telegram.org/bot{self.config.bot_token}/sendMessage"

        payload = {
            "chat_id": self.config.chat_id,
            "text": message,
            "parse_mode": "HTML",
        }

        try:
            async with self._session.post(url, data=payload) as response:
                if response.status != 200:
                    response_text = await response.text()
                    raise TelegramError(f"Telegram API error {response.status}: {response_text}")
        except aiohttp.ClientError as e:
            raise TelegramError(f"Failed to send Telegram message: {str(e)}") from e

    async def close(self) -> None:
        """Close the Telegram handler."""
        if self._session:
            await self._session.close()
            self._session = None
