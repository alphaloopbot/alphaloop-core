"""Logging-specific exceptions."""


class LoggingError(Exception):
    """Base exception for logging-related errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class HandlerError(LoggingError):
    """Exception raised for handler-related errors."""

    def __init__(self, message: str = "Handler operation failed.") -> None:
        super().__init__(message)


class FormatterError(LoggingError):
    """Exception raised for formatter-related errors."""

    def __init__(self, message: str = "Formatter operation failed.") -> None:
        super().__init__(message)


class TelegramError(HandlerError):
    """Exception raised for Telegram-specific errors."""

    def __init__(self, message: str = "Telegram operation failed.") -> None:
        super().__init__(message)
