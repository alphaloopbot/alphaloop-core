"""Infrastructure-specific exceptions."""

from .base import BaseException


class InfrastructureError(BaseException):
    """Base class for infrastructure errors."""

    def __init__(self, message: str, component: str | None = None) -> None:
        """Initialize infrastructure error."""
        super().__init__(message, code="INFRASTRUCTURE_ERROR")
        self.component = component


class DatabaseConnectionError(InfrastructureError):
    """Raised when database connection fails."""

    def __init__(self, message: str) -> None:
        """Initialize database connection error."""
        super().__init__(message, component="database")


class DatabaseQueryError(InfrastructureError):
    """Raised when database query fails."""

    def __init__(self, message: str) -> None:
        """Initialize database query error."""
        super().__init__(message, component="database")


class DatabaseTransactionError(InfrastructureError):
    """Raised when database transaction fails."""

    def __init__(self, message: str) -> None:
        """Initialize database transaction error."""
        super().__init__(message, component="database")


class DatabaseMigrationError(InfrastructureError):
    """Raised when database migration fails."""

    def __init__(self, message: str) -> None:
        """Initialize database migration error."""
        super().__init__(message, component="database")


class ExchangeConnectionError(InfrastructureError):
    """Raised when exchange connection fails."""

    def __init__(self, message: str, exchange: str | None = None) -> None:
        """Initialize exchange connection error."""
        super().__init__(message, component="exchange")
        self.exchange = exchange


class ExchangeApiError(InfrastructureError):
    """Raised when exchange API call fails."""

    def __init__(
        self, message: str, exchange: str | None = None, endpoint: str | None = None
    ) -> None:
        """Initialize exchange API error."""
        super().__init__(message, component="exchange")
        self.exchange = exchange
        self.endpoint = endpoint


class ExchangeRateLimitError(InfrastructureError):
    """Raised when exchange rate limit is exceeded."""

    def __init__(
        self, message: str, exchange: str | None = None, retry_after: int | None = None
    ) -> None:
        """Initialize exchange rate limit error."""
        super().__init__(message, component="exchange")
        self.exchange = exchange
        self.retry_after = retry_after


class ExternalApiError(InfrastructureError):
    """Raised when external API call fails."""

    def __init__(self, message: str, api: str | None = None, endpoint: str | None = None) -> None:
        """Initialize external API error."""
        super().__init__(message, component="external_api")
        self.api = api
        self.endpoint = endpoint


class MessageBrokerError(InfrastructureError):
    """Raised when message broker operations fail."""

    def __init__(self, message: str, broker: str | None = None) -> None:
        """Initialize message broker error."""
        super().__init__(message, component="message_broker")
        self.broker = broker


class RedisConnectionError(InfrastructureError):
    """Raised when Redis connection fails."""

    def __init__(self, message: str) -> None:
        """Initialize Redis connection error."""
        super().__init__(message, component="redis")


class StorageError(InfrastructureError):
    """Raised when storage operations fail."""

    def __init__(self, message: str, storage_type: str | None = None) -> None:
        """Initialize storage error."""
        super().__init__(message, component="storage")
        self.storage_type = storage_type


class FileSystemError(InfrastructureError):
    """Raised when file system operations fail."""

    def __init__(self, message: str, operation: str | None = None) -> None:
        """Initialize file system error."""
        super().__init__(message, component="file_system")
        self.operation = operation


class NetworkError(InfrastructureError):
    """Raised when network operations fail."""

    def __init__(self, message: str, host: str | None = None, port: int | None = None) -> None:
        """Initialize network error."""
        super().__init__(message, component="network")
        self.host = host
        self.port = port


class ConfigurationError(InfrastructureError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, config_key: str | None = None) -> None:
        """Initialize configuration error."""
        super().__init__(message, component="configuration")
        self.config_key = config_key


class ServiceDiscoveryError(InfrastructureError):
    """Raised when service discovery fails."""

    def __init__(self, message: str, service: str | None = None) -> None:
        """Initialize service discovery error."""
        super().__init__(message, component="service_discovery")
        self.service = service


class CircuitBreakerError(InfrastructureError):
    """Raised when circuit breaker is open."""

    def __init__(self, message: str, service: str | None = None) -> None:
        """Initialize circuit breaker error."""
        super().__init__(message, component="circuit_breaker")
        self.service = service


class HealthCheckError(InfrastructureError):
    """Raised when health check fails."""

    def __init__(self, message: str, service: str | None = None) -> None:
        """Initialize health check error."""
        super().__init__(message, component="health_check")
        self.service = service
