"""Logging configuration and settings."""

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class LogLevel(str, Enum):
    """Log levels enum."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class TelegramConfig:
    """Telegram configuration."""

    bot_token: str
    chat_id: int
    enabled: bool = True
    max_message_length: int = 3000
    send_on_error: bool = True
    send_on_warning: bool = True
    send_on_critical: bool = True
    send_on_info: bool = False
    send_on_debug: bool = False


@dataclass
class FileConfig:
    """File logging configuration."""

    logs_path: str | Path
    enabled: bool = True
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    rotation_enabled: bool = True


@dataclass
class ConsoleConfig:
    """Console logging configuration."""

    enabled: bool = True
    use_colors: bool = True
    show_timestamp: bool = True
    show_level: bool = True


@dataclass
class LoggingConfig:
    """Main logging configuration."""

    app_name: str
    log_level: LogLevel = LogLevel.INFO
    hostname: str = field(default_factory=lambda: os.getenv("HOSTNAME", "unknown"))

    # Handler configurations
    file_config: FileConfig | None = None
    telegram_config: TelegramConfig | None = None
    console_config: ConsoleConfig | None = None

    # Additional settings
    include_caller_info: bool = True
    truncate_long_messages: bool = True
    max_message_length: int = 3000

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if not self.app_name:
            raise ValueError("app_name is required")

        # Set default console config if none provided
        if self.console_config is None:
            self.console_config = ConsoleConfig()

    @classmethod
    def from_env(cls, app_name: str, **overrides: Any) -> "LoggingConfig":
        """Create configuration from environment variables."""
        # File configuration
        logs_path = os.getenv("LOGS_PATH", "./logs")
        file_config = FileConfig(logs_path=logs_path) if logs_path else None

        # Telegram configuration
        telegram_config = None
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id_str = os.getenv("TELEGRAM_LOG_CHAT_ID")

        if bot_token and chat_id_str:
            try:
                chat_id = int(chat_id_str)
                telegram_config = TelegramConfig(
                    bot_token=bot_token,
                    chat_id=chat_id,
                    enabled=os.getenv("TELEGRAM_LOGGING_ENABLED", "true").lower() == "true",
                )
            except ValueError:
                pass  # Invalid chat_id, skip telegram config

        # Log level
        log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        try:
            log_level = LogLevel(log_level_str)
        except ValueError:
            log_level = LogLevel.INFO

        config = cls(
            app_name=app_name,
            log_level=log_level,
            file_config=file_config,
            telegram_config=telegram_config,
            **overrides,
        )

        return config
