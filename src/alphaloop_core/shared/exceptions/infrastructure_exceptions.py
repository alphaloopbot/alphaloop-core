"""Infrastructure-specific exceptions."""

from .base import AlphaLoopError


class InfrastructureError(AlphaLoopError):
    """Raised for infrastructure-related issues."""

    def __init__(self, message: str, code: str | None = None) -> None:
        """Initialize infrastructure error."""
        super().__init__(message, code)


class DatabaseError(InfrastructureError):
    """Raised for database-related issues."""

    def __init__(self, message: str, code: str | None = None) -> None:
        """Initialize database error."""
        super().__init__(message, code)


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection or initialization fails."""

    def __init__(self, message: str, code: str | None = None) -> None:
        """Initialize database connection error."""
        super().__init__(message, code)


class ConnectionError(InfrastructureError):
    """Raised for connection-related issues."""

    def __init__(self, message: str, code: str | None = None) -> None:
        """Initialize connection error."""
        super().__init__(message, code)


class ExternalServiceError(InfrastructureError):
    """Raised for external service-related issues."""

    def __init__(self, message: str, code: str | None = None) -> None:
        """Initialize external service error."""
        super().__init__(message, code)
