"""Console logging handler."""

import sys
from typing import Any

from ..config.settings import ConsoleConfig
from ..formatters.console_formatter import ConsoleFormatter
from .base import BaseHandler


class ConsoleHandler(BaseHandler):
    """Handler for logging to console/stdout."""

    def __init__(self, config: ConsoleConfig) -> None:
        """
        Initialize console handler.

        Args:
            config: Console configuration.
        """
        formatter = ConsoleFormatter(
            use_colors=config.use_colors,
            show_timestamp=config.show_timestamp,
            show_level=config.show_level,
        )
        super().__init__(formatter)
        self.config = config

    async def emit(self, record: dict[str, Any]) -> None:
        """
        Write log record to console.

        Args:
            record: The log record dictionary.
        """
        if not self.config.enabled:
            return

        try:
            formatted_message = self.format_record(record)
            print(formatted_message, file=sys.stdout)
            sys.stdout.flush()
        except Exception:
            # Silently ignore console errors to avoid recursion
            pass

    async def close(self) -> None:
        """Close the console handler."""
        # Nothing to close for console handler
        pass
