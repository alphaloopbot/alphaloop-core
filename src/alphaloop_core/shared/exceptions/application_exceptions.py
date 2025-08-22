"""Application-specific exceptions."""

from .base import AlphaLoopError


class UseCaseError(AlphaLoopError):
    """Raised when a use-case execution fails."""

    def __init__(self, message: str, code: str | None = None) -> None:
        """Initialize use case error."""
        super().__init__(message, code)


class BusinessRuleError(UseCaseError):
    """Raised when a business rule is violated."""

    def __init__(self, message: str, rule: str | None = None) -> None:
        """Initialize business rule error."""
        super().__init__(message, code="BUSINESS_RULE_VIOLATION")
        self.rule = rule


class DataValidationError(UseCaseError):
    """Raised when data validation fails in a use case."""

    def __init__(self, message: str, field: str | None = None) -> None:
        """Initialize data validation error."""
        super().__init__(message, code="DATA_VALIDATION_ERROR")
        self.field = field


class ResourceNotFoundError(UseCaseError):
    """Raised when a required resource is not found."""

    def __init__(self, message: str, resource_type: str | None = None) -> None:
        """Initialize resource not found error."""
        super().__init__(message, code="RESOURCE_NOT_FOUND")
        self.resource_type = resource_type


class PermissionError(UseCaseError):
    """Raised when user lacks permission for an operation."""

    def __init__(self, message: str, operation: str | None = None) -> None:
        """Initialize permission error."""
        super().__init__(message, code="PERMISSION_DENIED")
        self.operation = operation


class ConcurrencyError(UseCaseError):
    """Raised when concurrent access conflicts occur."""

    def __init__(self, message: str, resource: str | None = None) -> None:
        """Initialize concurrency error."""
        super().__init__(message, code="CONCURRENCY_CONFLICT")
        self.resource = resource
