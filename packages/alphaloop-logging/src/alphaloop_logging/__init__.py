"""AlphaLoop Logging Package

Advanced logging package with multi-handler support, Telegram integration, and structured logging.
"""

__version__ = "0.1.0"
__author__ = "Didac Cristobal-Canals"
__email__ = "didac.crst@gmail.com"

from .config.settings import (
    ConsoleConfig,
    FileConfig,
    LoggingConfig,
    LogLevel,
    TelegramConfig,
)
from .core.logger import AlphaLoopLogger
from .exceptions import FormatterError, HandlerError, LoggingError
from .formatters.console_formatter import ConsoleFormatter
from .formatters.file_formatter import FileFormatter
from .formatters.telegram_formatter import TelegramFormatter
from .handlers.console_handler import ConsoleHandler
from .handlers.file_handler import FileHandler
from .handlers.telegram_handler import TelegramHandler

__all__ = [
    "AlphaLoopLogger",
    "FileHandler",
    "TelegramHandler",
    "ConsoleHandler",
    "TelegramFormatter",
    "FileFormatter",
    "ConsoleFormatter",
    "LoggingConfig",
    "LogLevel",
    "FileConfig",
    "TelegramConfig",
    "ConsoleConfig",
    "LoggingError",
    "HandlerError",
    "FormatterError",
]
