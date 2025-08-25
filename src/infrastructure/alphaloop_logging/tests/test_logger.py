"""Tests for AlphaLoop logger."""

from pathlib import Path
import tempfile
from unittest.mock import AsyncMock, Mock, patch

from alphaloop_logging import (
    AlphaLoopLogger,
    FileConfig,
    LoggingConfig,
    LogLevel,
    TelegramConfig,
)
import pytest


class TestAlphaLoopLogger:
    """Test cases for AlphaLoopLogger."""

    def test_logger_initialization(self):
        """Test logger initialization."""
        config = LoggingConfig(app_name="test-app")
        logger = AlphaLoopLogger(config)

        assert logger.config.app_name == "test-app"
        assert len(logger.handlers) >= 1  # At least console handler

    @pytest.mark.asyncio
    async def test_basic_logging(self):
        """Test basic logging functionality."""
        config = LoggingConfig(app_name="test-app")
        logger = AlphaLoopLogger(config)

        # Test different log levels
        await logger.debug("Debug message")
        await logger.info("Info message")
        await logger.warning("Warning message")
        await logger.error("Error message")
        await logger.critical("Critical message")

        await logger.close()

    @pytest.mark.asyncio
    async def test_file_logging(self):
        """Test file logging with temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_config = FileConfig(logs_path=temp_dir)
            config = LoggingConfig(app_name="test-app", file_config=file_config)
            logger = AlphaLoopLogger(config)

            await logger.info("Test message")
            await logger.close()

            # Check if log file was created
            log_files = list(Path(temp_dir).glob("test-app_*.log"))
            assert len(log_files) == 1

            # Check file content
            with open(log_files[0]) as f:
                content = f.read()
                assert "Test message" in content

    @pytest.mark.asyncio
    async def test_telegram_handler_selection(self):
        """Test telegram handler message selection."""
        telegram_config = TelegramConfig(
            bot_token="fake-token",
            chat_id=123456,
            send_on_error=True,
            send_on_info=False,
        )
        config = LoggingConfig(app_name="test-app", telegram_config=telegram_config)
        logger = AlphaLoopLogger(config)

        # Find telegram handler
        telegram_handler = None
        for handler in logger.handlers:
            if hasattr(handler, "config") and hasattr(handler.config, "bot_token"):
                telegram_handler = handler
                break

        assert telegram_handler is not None

        # Test message selection
        error_record = {"level": "ERROR", "message": "Test error"}
        info_record = {"level": "INFO", "message": "Test info"}

        assert telegram_handler.should_handle(error_record) is True
        assert telegram_handler.should_handle(info_record) is False

        await logger.close()

    @pytest.mark.asyncio
    async def test_legacy_compatibility(self):
        """Test legacy Logger compatibility."""
        config = LoggingConfig(app_name="test-app")
        logger = AlphaLoopLogger(config)

        # Test legacy-style calls
        await logger("Error message", info="context", level="E")
        await logger.log("Info message", level="I", info="test")
        await logger.launch("Test Application")

        await logger.close()

    @pytest.mark.asyncio
    async def test_structured_logging(self):
        """Test structured logging with extra fields."""
        config = LoggingConfig(app_name="test-app")
        logger = AlphaLoopLogger(config)

        await logger.info(
            "User action",
            info="user_service",
            user_id="12345",
            action="login",
            ip_address="192.168.1.100",
        )

        await logger.close()

    @pytest.mark.asyncio
    async def test_message_truncation(self):
        """Test message truncation."""
        config = LoggingConfig(
            app_name="test-app", max_message_length=50, truncate_long_messages=True
        )
        logger = AlphaLoopLogger(config)

        long_message = "x" * 100
        record = logger._create_record("INFO", long_message)

        assert len(record["message"]) <= 53  # 50 + "..."
        assert record["message"].endswith("...")

        await logger.close()

    def test_config_from_env(self):
        """Test configuration from environment variables."""
        with patch.dict(
            "os.environ",
            {
                "LOGS_PATH": "./test-logs",
                "LOG_LEVEL": "DEBUG",
                "TELEGRAM_BOT_TOKEN": "test-token",
                "TELEGRAM_LOG_CHAT_ID": "123456",
                "HOSTNAME": "test-host",
            },
        ):
            config = LoggingConfig.from_env("test-app")

            assert config.app_name == "test-app"
            assert config.log_level == LogLevel.DEBUG
            assert config.hostname == "test-host"
            assert config.file_config is not None
            assert config.file_config.logs_path == "./test-logs"
            assert config.telegram_config is not None
            assert config.telegram_config.bot_token == "test-token"
            assert config.telegram_config.chat_id == 123456

    @pytest.mark.asyncio
    async def test_telegram_override(self):
        """Test telegram override functionality."""
        telegram_config = TelegramConfig(bot_token="fake-token", chat_id=123456, send_on_info=False)
        config = LoggingConfig(app_name="test-app", telegram_config=telegram_config)
        logger = AlphaLoopLogger(config)

        # Find telegram handler
        telegram_handler = None
        for handler in logger.handlers:
            if hasattr(handler, "config") and hasattr(handler.config, "bot_token"):
                telegram_handler = handler
                break

        assert telegram_handler is not None

        # Test override behavior
        info_record_force = {"level": "INFO", "message": "Test", "telegram": True}
        info_record_block = {"level": "INFO", "message": "Test", "telegram": False}
        info_record_default = {"level": "INFO", "message": "Test"}

        assert telegram_handler.should_handle(info_record_force) is True
        assert telegram_handler.should_handle(info_record_block) is False
        assert telegram_handler.should_handle(info_record_default) is False

        await logger.close()

    @pytest.mark.asyncio
    async def test_error_resilience(self):
        """Test that logging errors don't break the application."""
        # Create a mock handler that always fails
        failing_handler = Mock()
        failing_handler.should_handle = Mock(return_value=True)
        failing_handler.emit = AsyncMock(side_effect=Exception("Handler failed"))
        failing_handler.close = AsyncMock()

        config = LoggingConfig(app_name="test-app")
        logger = AlphaLoopLogger(config)
        logger.handlers.append(failing_handler)

        # This should not raise an exception
        await logger.info("Test message")

        await logger.close()
