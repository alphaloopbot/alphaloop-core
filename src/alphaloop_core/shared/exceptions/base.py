"""Base exception class for shared exceptions."""


class BaseException(Exception):
    """Base exception class with common functionality."""

    def __init__(self, message: str, code: str | None = None) -> None:
        """Initialize base exception."""
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self) -> str:
        """String representation."""
        return self.message

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"{self.__class__.__name__}(message='{self.message}', code='{self.code}')"
