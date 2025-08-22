"""Custom exceptions for AlphaLoop Storage package."""


class StorageError(Exception):
    """Base exception for all storage-related errors."""

    pass


class DatabaseConnectionError(StorageError):
    """Raised when database connection fails."""

    pass


class DatabaseQueryError(StorageError):
    """Raised when database query execution fails."""

    pass


class SchemaError(StorageError):
    """Raised when schema operations fail."""

    pass


class TableError(StorageError):
    """Raised when table operations fail."""

    pass


class DataValidationError(StorageError):
    """Raised when data validation fails."""

    pass


class ConfigurationError(StorageError):
    """Raised when configuration is invalid."""

    pass


class MigrationError(StorageError):
    """Raised when database migration fails."""

    pass


class LifecycleError(StorageError):
    """Raised when data lifecycle operations fail."""

    pass
