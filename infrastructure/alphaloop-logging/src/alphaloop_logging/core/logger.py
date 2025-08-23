"""
Main AlphaLoop logger implementation.

This module provides the core logging functionality for the AlphaLoop system,
offering structured logging with multiple output handlers and advanced features
for monitoring and debugging distributed systems.

The logger supports multiple output destinations simultaneously, including
console output, file logging, and Telegram notifications, with configurable
formats and filtering capabilities.

Key Features:
- Multi-handler logging (console, file, Telegram)
- Structured logging with metadata
- Async support for non-blocking operations
- Configurable message formatting
- Caller information tracking
- Message truncation and filtering
- Telegram integration for alerts
"""

import asyncio
import inspect
from datetime import datetime
from typing import Any

from ..config.settings import LoggingConfig, LogLevel
from ..handlers.base import BaseHandler
from ..handlers.console_handler import ConsoleHandler
from ..handlers.file_handler import FileHandler
from ..handlers.telegram_handler import TelegramHandler


class AlphaLoopLogger:
    """
    Main AlphaLoop logger with multi-handler support.

    This class provides comprehensive logging capabilities for the AlphaLoop system,
    supporting multiple output destinations simultaneously with structured logging
    and advanced features for monitoring and debugging distributed systems.

    The logger can output to console, files, and Telegram simultaneously, with
    configurable formats, filtering, and async support for non-blocking operations.

    Key Features:
    - Multi-handler logging (console, file, Telegram)
    - Structured logging with metadata
    - Async support for non-blocking operations
    - Configurable message formatting
    - Caller information tracking
    - Message truncation and filtering
    - Telegram integration for alerts

    Usage:
        config = LoggingConfig.from_env(app_name="my-service")
        logger = AlphaLoopLogger(config)
        await logger.info("Service started successfully")
        await logger.error("Connection failed", extra={"retry_count": 3})
    """

    def __init__(self, config: LoggingConfig) -> None:
        """
        Initialize AlphaLoop logger.

        Creates a new logger instance with the specified configuration. The logger
        will automatically set up handlers based on the configuration and prepare
        for logging operations.

        Args:
            config: Logging configuration containing handler settings and behavior
                   parameters

        Example:
            >>> config = LoggingConfig.from_env(app_name="my-service")
            >>> logger = AlphaLoopLogger(config)
            >>> # Logger is ready to use
        """
        self.config = config
        self.handlers: list[BaseHandler] = []
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """
        Setup all configured handlers.

        Initializes and configures all logging handlers based on the logger
        configuration. This method is called during initialization and sets up
        console, file, and Telegram handlers as specified in the config.

        The method creates handler instances and adds them to the internal
        handlers list for use during logging operations.
        """
        # Console handler
        if self.config.console_config:
            console_handler = ConsoleHandler(self.config.console_config)
            self.handlers.append(console_handler)

        # File handler
        if self.config.file_config:
            file_handler = FileHandler(self.config.file_config, self.config.app_name)
            self.handlers.append(file_handler)

        # Telegram handler
        if self.config.telegram_config:
            telegram_handler = TelegramHandler(
                self.config.telegram_config, self.config.hostname
            )
            self.handlers.append(telegram_handler)

    def _get_caller_info(self) -> dict[str, str]:
        """
        Get information about the calling function.

        Extracts information about the function that called the logging method,
        including module name, function name, and line number. This information
        is useful for debugging and tracing log messages back to their source.

        Returns:
            Dictionary containing caller information:
            - module: Name of the calling module
            - function: Name of the calling function
            - line: Line number where the logging call was made

        Example:
            >>> info = logger._get_caller_info()
            >>> print(info)
            {'module': 'my_module', 'function': 'process_data', 'line': '42'}
        """
        if not self.config.include_caller_info:
            return {}

        # Get the calling frame (skip current frame and the public method frame)
        frame = inspect.currentframe()
        if frame and frame.f_back and frame.f_back.f_back:
            caller_frame = frame.f_back.f_back
            return {
                "module": caller_frame.f_globals.get("__name__", "unknown"),
                "function": caller_frame.f_code.co_name,
                "line": str(caller_frame.f_lineno),
            }
        return {}

    def _create_record(
        self,
        level: str,
        message: str,
        info: str = "",
        telegram: bool | None = None,
        **extra: Any,
    ) -> dict[str, Any]:
        """
        Create a log record.

        Args:
            level: Log level.
            message: Log message.
            info: Additional context information.
            telegram: Override telegram sending behavior.
            **extra: Additional fields.

        Returns:
            Log record dictionary.
        """
        # Truncate message if configured
        if self.config.truncate_long_messages:
            message = self._truncate_message(message)

        # Get caller information
        caller_info = self._get_caller_info()

        record = {
            "timestamp": datetime.now(),
            "level": level.upper(),
            "message": message,
            "app_name": self.config.app_name,
            "hostname": self.config.hostname,
            "info": info,
            "telegram": telegram,
            **caller_info,
            **extra,
        }

        return record

    def _truncate_message(self, message: str) -> str:
        """Truncate message if it's too long."""
        max_length = self.config.max_message_length
        if len(message) <= max_length:
            return message
        return f"{message[:max_length]}..."

    async def _emit_to_handlers(self, record: dict[str, Any]) -> None:
        """
        Emit record to all handlers.

        Args:
            record: The log record to emit.
        """
        tasks = []
        for handler in self.handlers:
            if handler.should_handle(record):
                tasks.append(handler.emit(record))

        if tasks:
            # Run all handlers concurrently
            await asyncio.gather(*tasks, return_exceptions=True)

    # Public logging methods

    async def debug(
        self, message: str, info: str = "", telegram: bool | None = None, **extra: Any
    ) -> None:
        """Log a debug message."""
        record = self._create_record(LogLevel.DEBUG, message, info, telegram, **extra)
        await self._emit_to_handlers(record)

    async def info(
        self, message: str, info: str = "", telegram: bool | None = None, **extra: Any
    ) -> None:
        """Log an info message."""
        record = self._create_record(LogLevel.INFO, message, info, telegram, **extra)
        await self._emit_to_handlers(record)

    async def warning(
        self, message: str, info: str = "", telegram: bool | None = None, **extra: Any
    ) -> None:
        """Log a warning message."""
        record = self._create_record(LogLevel.WARNING, message, info, telegram, **extra)
        await self._emit_to_handlers(record)

    async def error(
        self, message: str, info: str = "", telegram: bool | None = None, **extra: Any
    ) -> None:
        """Log an error message."""
        record = self._create_record(LogLevel.ERROR, message, info, telegram, **extra)
        await self._emit_to_handlers(record)

    async def critical(
        self, message: str, info: str = "", telegram: bool | None = None, **extra: Any
    ) -> None:
        """Log a critical message."""
        record = self._create_record(
            LogLevel.CRITICAL, message, info, telegram, **extra
        )
        await self._emit_to_handlers(record)

    # Convenience methods for compatibility with legacy Logger

    async def launch(self, name: str) -> None:
        """Log a launch message (for compatibility)."""
        await self.info(f"Launching {name}")

    async def log(
        self,
        message: str,
        level: str = "INFO",
        info: str = "",
        telegram: bool | None = None,
        **extra: Any,
    ) -> None:
        """
        Generic log method (for compatibility with legacy Logger).

        Args:
            message: Log message.
            level: Log level (E, W, I, C, D or full names).
            info: Additional context information.
            telegram: Override telegram sending behavior.
            **extra: Additional fields.
        """
        # Map legacy level codes to full names
        level_map = {
            "E": LogLevel.ERROR,
            "W": LogLevel.WARNING,
            "I": LogLevel.INFO,
            "C": LogLevel.CRITICAL,
            "D": LogLevel.DEBUG,
        }

        # Convert level
        full_level = level_map.get(level.upper(), level.upper())

        # Route to appropriate method
        if full_level == LogLevel.DEBUG:
            await self.debug(message, info, telegram, **extra)
        elif full_level == LogLevel.INFO:
            await self.info(message, info, telegram, **extra)
        elif full_level == LogLevel.WARNING:
            await self.warning(message, info, telegram, **extra)
        elif full_level == LogLevel.ERROR:
            await self.error(message, info, telegram, **extra)
        elif full_level == LogLevel.CRITICAL:
            await self.critical(message, info, telegram, **extra)
        else:
            await self.info(message, info, telegram, **extra)

    # Callable interface for legacy compatibility
    async def __call__(
        self,
        msg: str,
        info: str = "",
        level: str = "E",
        telegram: bool | None = None,
        **extra: Any,
    ) -> None:
        """
        Callable interface for compatibility with legacy Logger.

        Args:
            msg: Log message.
            info: Additional context information.
            level: Log level code (E, W, I, C, D).
            telegram: Override telegram sending behavior.
            **extra: Additional fields.
        """
        await self.log(msg, level, info, telegram, **extra)

    async def close(self) -> None:
        """Close all handlers and clean up resources."""
        for handler in self.handlers:
            await handler.close()
        self.handlers.clear()
