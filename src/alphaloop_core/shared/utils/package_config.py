"""Package configuration utilities for AlphaLoop Core."""

from functools import lru_cache
from typing import Any

from infrastructure.alphaloop_cache import CacheConfig
from infrastructure.alphaloop_heartbeat import HeartbeatSettings
from infrastructure.alphaloop_logging import LoggingConfig
from infrastructure.alphaloop_storage import DatabaseConfig

# Note: alphaloop-security doesn't have a config class, it uses direct initialization


@lru_cache
def get_cache_config() -> CacheConfig:
    """Get cache configuration using alphaloop-cache."""
    return CacheConfig.from_env(prefix="CACHE_")


@lru_cache
def get_heartbeat_config() -> HeartbeatSettings:
    """Get heartbeat configuration using alphaloop-heartbeat."""
    return HeartbeatSettings()


@lru_cache
def get_logging_config() -> LoggingConfig:
    """Get logging configuration using alphaloop-logging."""
    return LoggingConfig.from_env(app_name="alphaloop-core")


@lru_cache
def get_storage_config() -> DatabaseConfig:
    """Get storage configuration using alphaloop-storage."""
    return DatabaseConfig.from_env(prefix="DATABASE_")


@lru_cache
def get_security_config() -> dict[str, Any]:
    """Get security configuration (alphaloop-security uses direct initialization)."""
    import os

    from dotenv import load_dotenv

    load_dotenv()

    return {
        "secret_key": os.getenv("SECURITY_SECRET_KEY", "default-secret-key"),
        "encryption_key": os.getenv("SECURITY_ENCRYPTION_KEY", "default-encryption-key"),
        "hash_salt": os.getenv("SECURITY_HASH_SALT", "default-salt"),
        "time_window": int(os.getenv("SECURITY_TIME_WINDOW", "300")),
    }


@lru_cache
def get_all_package_configs() -> dict[str, Any]:
    """Get all package configurations."""
    return {
        "cache": get_cache_config(),
        "heartbeat": get_heartbeat_config(),
        "logging": get_logging_config(),
        "security": get_security_config(),
        "storage": get_storage_config(),
    }
