"""Custom exceptions for AlphaLoop Cache package."""


class CacheError(Exception):
    """Base exception for all cache-related errors."""

    pass


class CacheConnectionError(CacheError):
    """Raised when cache connection fails."""

    pass


class CacheOperationError(CacheError):
    """Raised when cache operation fails."""

    pass


class CacheKeyError(CacheError):
    """Raised when cache key is invalid or missing."""

    pass


class CacheSerializationError(CacheError):
    """Raised when data serialization/deserialization fails."""

    pass


class PubSubError(CacheError):
    """Raised when pub/sub operations fail."""

    pass


class ConfigurationError(CacheError):
    """Raised when cache configuration is invalid."""

    pass
