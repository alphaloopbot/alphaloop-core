"""Configuration utilities for shared utils."""

import os
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv

from ..exceptions.infrastructure_exceptions import ConfigurationError


def load_environment() -> None:
    """Load environment variables from .env files."""
    # Try to load .env from multiple possible locations
    env_paths = [
        ".env",
        "../.env",
        "../../.env",
        "/opt/app/.env",
        "/.env",
    ]

    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            break


@lru_cache
def get_database_url() -> str:
    """Get the database URL from environment variables (DEPRECATED: Use alphaloop-storage package)."""
    import warnings

    warnings.warn(
        "get_database_url() is deprecated. Use alphaloop_core.get_storage_config() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    from alphaloop_core import get_storage_config

    config = get_storage_config()
    return config.async_url


@lru_cache
def get_redis_url() -> str:
    """Get the Redis URL from environment variables (DEPRECATED: Use alphaloop-cache package)."""
    import warnings

    warnings.warn(
        "get_redis_url() is deprecated. Use alphaloop_core.get_cache_config() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    from alphaloop_core import get_cache_config

    config = get_cache_config()
    return config.connection_url


@lru_cache
def get_rabbitmq_url() -> str:
    """Get the RabbitMQ URL from environment variables."""
    load_environment()

    rabbitmq_url = os.getenv("RABBITMQ_URL")
    if rabbitmq_url:
        return rabbitmq_url

    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = os.getenv("RABBITMQ_PORT", "5672")
    user = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASSWORD", "guest")
    vhost = os.getenv("RABBITMQ_VHOST", "/")

    # Percent-encode vhost to support "/" and special characters
    from urllib.parse import quote

    return f"amqp://{user}:{password}@{host}:{port}/{quote(vhost, safe='')}"


@lru_cache
def get_service_config() -> dict[str, Any]:
    """Get service configuration from environment variables."""
    load_environment()

    return {
        "SERVICE_HOST": os.getenv("SERVICE_HOST", "localhost"),
        "SERVICE_PORT": int(os.getenv("SERVICE_PORT", "8000")),
        "SERVICE_URL": os.getenv("SERVICE_URL"),
        "API_KEY": os.getenv("API_KEY", "dev-key"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
    }


@lru_cache
def get_exchange_config() -> dict[str, Any]:
    """Get exchange configuration from environment variables."""
    load_environment()

    return {
        "BINANCE_API_KEY": os.getenv("BINANCE_API_KEY"),
        "BINANCE_SECRET_KEY": os.getenv("BINANCE_SECRET_KEY"),
        "COINBASE_API_KEY": os.getenv("COINBASE_API_KEY"),
        "COINBASE_SECRET_KEY": os.getenv("COINBASE_SECRET_KEY"),
        "KRAKEN_API_KEY": os.getenv("KRAKEN_API_KEY"),
        "KRAKEN_SECRET_KEY": os.getenv("KRAKEN_SECRET_KEY"),
        "EXCHANGE_RATE_LIMIT": int(os.getenv("EXCHANGE_RATE_LIMIT", "100")),
        "EXCHANGE_TIMEOUT": int(os.getenv("EXCHANGE_TIMEOUT", "30")),
    }


@lru_cache
def get_telegram_config() -> dict[str, Any]:
    """Get Telegram configuration from environment variables."""
    load_environment()

    return {
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
        "TELEGRAM_ENABLED": os.getenv("TELEGRAM_ENABLED", "false").lower() == "true",
    }


@lru_cache
def get_storage_config() -> dict[str, Any]:
    """Get storage configuration from environment variables."""
    load_environment()

    return {
        "STORAGE_TYPE": os.getenv("STORAGE_TYPE", "local"),
        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "AWS_REGION": os.getenv("AWS_REGION", "us-east-1"),
        "AWS_S3_BUCKET": os.getenv("AWS_S3_BUCKET"),
        "GCS_BUCKET": os.getenv("GCS_BUCKET"),
        "GCS_CREDENTIALS_FILE": os.getenv("GCS_CREDENTIALS_FILE"),
    }


def get_config_value(key: str, default: Any = None, required: bool = False) -> Any:
    """Get a configuration value by key."""
    load_environment()

    value = os.getenv(key, default)

    if required and value is None:
        raise ConfigurationError(f"Required configuration key '{key}' is missing")

    return value


def get_config_section(prefix: str) -> dict[str, Any]:
    """Get all configuration values with a specific prefix."""
    load_environment()

    section = {}
    for key, value in os.environ.items():
        if key.startswith(prefix):
            section[key[len(prefix) :]] = value

    return section


def validate_required_config(required_keys: list[str]) -> None:
    """Validate that all required configuration keys are present."""
    load_environment()

    missing_keys = []
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)

    if missing_keys:
        raise ConfigurationError(f"Missing required configuration keys: {', '.join(missing_keys)}")


def get_environment() -> str:
    """Get the current environment."""
    return get_config_value("ENVIRONMENT", "development")


def is_development() -> bool:
    """Check if running in development environment."""
    return get_environment() == "development"


def is_production() -> bool:
    """Check if running in production environment."""
    return get_environment() == "production"


def is_testing() -> bool:
    """Check if running in testing environment."""
    return get_environment() == "testing"
