"""Unit tests for the config module."""

import os
from unittest.mock import patch

from alphaloop_core.config import get_default_currency, settings
from alphaloop_core.shared.types.enums import Currency


class TestConfig:
    """Test configuration functionality."""

    def test_settings_defaults(self) -> None:
        """Test that settings returns expected defaults."""
        with patch.dict(os.environ, {}, clear=True):
            config = settings()

            assert config["SERVICE_URL"] == "http://localhost:8000"
            assert config["API_KEY"] == "dev-key"
            assert config["LOG_LEVEL"] == "INFO"
            assert config["ENVIRONMENT"] == "development"
            assert config["DB_HOST"] == "localhost"
            assert config["DB_PORT"] == "5432"
            assert config["DB_NAME"] == "alphaloop"

    def test_settings_environment_override(self) -> None:
        """Test that environment variables override defaults."""
        test_env = {
            "SERVICE_HOST": "test-host",
            "SERVICE_PORT": "9000",
            "API_KEY": "test-key",
            "LOG_LEVEL": "DEBUG",
            "ENVIRONMENT": "production",
        }

        # Clear the cache to ensure fresh settings
        settings.cache_clear()

        with patch.dict(os.environ, test_env, clear=True):
            config = settings()

            assert config["SERVICE_URL"] == "http://test-host:9000"
            assert config["API_KEY"] == "test-key"
            assert config["LOG_LEVEL"] == "DEBUG"
            assert config["ENVIRONMENT"] == "production"

    def test_settings_service_url_override(self) -> None:
        """Test that SERVICE_URL can override automatic construction."""
        test_env = {
            "SERVICE_URL": "https://custom-service.com",
            "SERVICE_HOST": "ignored-host",
            "SERVICE_PORT": "ignored-port",
        }

        # Clear the cache to ensure fresh settings
        settings.cache_clear()

        with patch.dict(os.environ, test_env, clear=True):
            config = settings()

            assert config["SERVICE_URL"] == "https://custom-service.com"

    def test_settings_caching(self) -> None:
        """Test that settings are cached."""
        config1 = settings()
        config2 = settings()

        # Should be the same object due to caching
        assert config1 is config2

    def test_default_currency_configuration(self) -> None:
        """Test default currency configuration."""
        settings.cache_clear()
        # Test default value
        currency = get_default_currency()
        assert currency == Currency.USDT

    def test_default_currency_override(self) -> None:
        """Test default currency can be overridden."""
        settings.cache_clear()
        with patch.dict(os.environ, {"DEFAULT_CURRENCY": "BTC"}):
            currency = get_default_currency()
            assert currency == Currency.BTC

    def test_default_currency_invalid_fallback(self) -> None:
        """Test fallback to USDT for invalid currency."""
        settings.cache_clear()
        with patch.dict(os.environ, {"DEFAULT_CURRENCY": "INVALID"}):
            currency = get_default_currency()
            assert currency == Currency.USDT
