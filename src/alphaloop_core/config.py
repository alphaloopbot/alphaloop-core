"""Centralized configuration management for AlphaLoop Core."""

from functools import lru_cache
import os
from pathlib import Path
from types import MappingProxyType

from dotenv import load_dotenv

from alphaloop_core.shared.types.enums import Currency

# Try to load .env from multiple possible locations
env_paths = [
    Path(__file__).parent.parent.parent / ".env",  # From package root
    Path("/opt/app/.env"),  # From container root
    Path("/.env"),  # From container root (alternative)
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break


@lru_cache
def settings() -> MappingProxyType[str, str]:
    """Get application settings from environment variables."""
    # Automatic URL construction from HOST:PORT variables
    service_host = os.getenv("SERVICE_HOST", "localhost")
    service_port = os.getenv("SERVICE_PORT", "8000")

    # Allow manual override with SERVICE_URL if needed
    service_url_env = os.getenv("SERVICE_URL")

    service_url = (
        service_url_env
        if service_url_env and service_url_env.strip()
        else f"http://{service_host}:{service_port}"
    )

    cfg = {
        "SERVICE_URL": service_url,
        "API_KEY": os.getenv("API_KEY", "dev-key"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
        "DB_HOST": os.getenv("DB_HOST", "localhost"),
        "DB_PORT": os.getenv("DB_PORT", "5432"),
        "DB_NAME": os.getenv("DB_NAME", "alphaloop"),
        "DB_USER": os.getenv("DB_USER", "postgres"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD", "password"),
        # DATABASE_URL fallback composed from individual DB_* vars to prevent drift
        "DATABASE_URL": os.getenv(
            "DATABASE_URL",
            f"postgresql://{os.getenv('DB_USER', 'postgres')}:"
            f"{os.getenv('DB_PASSWORD', 'password')}"
            f"@{os.getenv('DB_HOST', 'localhost')}:"
            f"{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'alphaloop')}",
        ),
        # Default currency for market data and trading operations
        "DEFAULT_CURRENCY": os.getenv("DEFAULT_CURRENCY", "USDT").strip().upper(),
    }
    return MappingProxyType(cfg)


def get_default_currency() -> Currency:
    """Get the default currency from configuration."""
    currency_str = settings()["DEFAULT_CURRENCY"].strip().upper()
    try:
        return Currency(currency_str)
    except ValueError:
        # Fallback to USDT if invalid currency is configured
        import logging

        logging.warning(f"Invalid currency code '{currency_str}', falling back to USDT")
        return Currency.USDT
