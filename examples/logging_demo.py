#!/usr/bin/env python3
"""
Logging Package Demo

This script demonstrates the usage of the AlphaLoop Logging package
with file logging, console output, and Telegram integration.
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Add the infrastructure directory to the path
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "infrastructure", "alphaloop-logging", "src")
)

from alphaloop_logging import (
    AlphaLoopLogger,
    ConsoleConfig,
    FileConfig,
    LoggingConfig,
    LogLevel,
    TelegramConfig,
)


async def demo_basic_logging():
    """Demonstrate basic logging functionality."""
    print("🔧 Basic Logging Demo")
    print("=" * 50)

    # Create simple configuration
    config = LoggingConfig(
        app_name="demo-app",
        log_level=LogLevel.DEBUG,
        console_config=ConsoleConfig(enabled=True, use_colors=True, show_timestamp=True),
    )

    logger = AlphaLoopLogger(config)

    # Test different log levels
    await logger.debug("This is a debug message", info="debug_test")
    await logger.info("Application started successfully", info="startup")
    await logger.warning("This is a warning message", info="warning_test")
    await logger.error("An error occurred", info="error_test")
    await logger.critical("Critical system error", info="critical_test")

    # Test launch method
    await logger.launch("Demo Application")

    await logger.close()
    print("✅ Basic logging demo completed\n")


async def demo_file_logging():
    """Demonstrate file logging with rotation."""
    print("📁 File Logging Demo")
    print("=" * 50)

    # Create temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📂 Logging to: {temp_dir}")

        # Create configuration with file logging
        config = LoggingConfig(
            app_name="file-demo",
            log_level=LogLevel.INFO,
            file_config=FileConfig(
                logs_path=temp_dir,
                max_file_size=1024,  # Small size for demo
                backup_count=3,
                rotation_enabled=True,
            ),
            console_config=ConsoleConfig(enabled=False),  # Disable console for this demo
        )

        logger = AlphaLoopLogger(config)

        # Generate some log entries
        for i in range(10):
            await logger.info(f"Log entry number {i+1}", info=f"iteration_{i+1}")
            # Add some bulk to trigger rotation
            await logger.info("x" * 100, info="bulk_data")

        await logger.close()

        # Show created files
        log_files = list(Path(temp_dir).glob("*.log"))
        print(f"📄 Created {len(log_files)} log file(s):")
        for log_file in sorted(log_files):
            size = log_file.stat().st_size
            print(f"   • {log_file.name} ({size} bytes)")

        # Show sample content
        if log_files:
            print("\n📖 Sample log content:")
            with open(log_files[0]) as f:
                lines = f.readlines()[:3]
                for line in lines:
                    print(f"   {line.strip()}")

    print("✅ File logging demo completed\n")


async def demo_structured_logging():
    """Demonstrate structured logging with extra fields."""
    print("📊 Structured Logging Demo")
    print("=" * 50)

    config = LoggingConfig(
        app_name="structured-demo",
        log_level=LogLevel.INFO,
        console_config=ConsoleConfig(enabled=True, use_colors=True),
    )

    logger = AlphaLoopLogger(config)

    # Structured log entries with extra fields
    await logger.info(
        "User login successful",
        info="authentication",
        user_id="12345",
        username="john_doe",
        ip_address="192.168.1.100",
        login_method="password",
        session_id="abc123",
    )

    await logger.warning(
        "High memory usage detected",
        info="system_monitor",
        memory_usage_percent=85.5,
        available_memory_mb=512,
        process_count=42,
        alert_threshold=80.0,
    )

    await logger.error(
        "Database connection failed",
        info="database_manager",
        host="localhost",
        port=5432,
        database="production",
        retry_count=3,
        error_code="CONNECTION_TIMEOUT",
    )

    await logger.close()
    print("✅ Structured logging demo completed\n")


async def demo_legacy_compatibility():
    """Demonstrate legacy Logger compatibility."""
    print("🔄 Legacy Compatibility Demo")
    print("=" * 50)

    config = LoggingConfig(app_name="legacy-demo")
    logger = AlphaLoopLogger(config)

    # Legacy-style usage
    await logger("Error message using legacy style", info="legacy_test", level="E")
    await logger("Warning message using legacy style", info="legacy_test", level="W")
    await logger("Info message using legacy style", info="legacy_test", level="I")
    await logger("Debug message using legacy style", info="legacy_test", level="D")
    await logger("Critical message using legacy style", info="legacy_test", level="C")

    # Legacy launch method
    await logger.launch("Legacy Application")

    # Legacy log method
    await logger.log("Generic log message", level="INFO", info="generic_test")

    await logger.close()
    print("✅ Legacy compatibility demo completed\n")


async def demo_telegram_simulation():
    """Demonstrate Telegram integration (simulated)."""
    print("💬 Telegram Integration Demo (Simulated)")
    print("=" * 50)

    # Note: This uses fake credentials for demo purposes
    telegram_config = TelegramConfig(
        bot_token="demo-token-not-real",
        chat_id=123456789,
        enabled=False,  # Disabled for demo
        send_on_error=True,
        send_on_warning=True,
        send_on_critical=True,
        send_on_info=False,
    )

    config = LoggingConfig(
        app_name="telegram-demo",
        hostname="demo-rpi-01",
        telegram_config=telegram_config,
        console_config=ConsoleConfig(enabled=True),
    )

    logger = AlphaLoopLogger(config)

    print("📝 The following would be sent to Telegram (if enabled):")

    # These would normally be sent to Telegram
    await logger.error(
        "Service connection lost", info="network_monitor", telegram=False
    )  # Force disable for demo
    await logger.critical(
        "System overheating detected", info="temperature_monitor", telegram=False
    )  # Force disable for demo
    await logger.warning(
        "High CPU usage", info="system_monitor", telegram=False
    )  # Force disable for demo

    # This would not be sent (INFO level)
    await logger.info("Regular status update", info="status_check")

    # Force send to Telegram (if enabled)
    await logger.info(
        "Important announcement", info="admin", telegram=False
    )  # Force disable for demo

    await logger.close()
    print("✅ Telegram integration demo completed\n")


async def demo_error_resilience():
    """Demonstrate error resilience."""
    print("🛡️ Error Resilience Demo")
    print("=" * 50)

    config = LoggingConfig(app_name="resilience-demo")
    logger = AlphaLoopLogger(config)

    print("📝 Testing logging with various scenarios...")

    # Normal logging
    await logger.info("Normal log message")

    # Very long message (truncation test)
    long_message = "Very long message: " + "x" * 5000
    await logger.info(long_message, info="truncation_test")

    # Special characters
    await logger.info("Message with special chars: <>&\"'", info="special_chars")

    # Unicode characters
    await logger.info("Unicode message: 🚀 ñáéíóú 中文 русский", info="unicode_test")

    # Empty message
    await logger.info("", info="empty_message")

    await logger.close()
    print("✅ Error resilience demo completed\n")


async def demo_configuration_options():
    """Demonstrate different configuration options."""
    print("⚙️ Configuration Options Demo")
    print("=" * 50)

    # Minimal configuration
    print("🔹 Minimal configuration:")
    config1 = LoggingConfig(app_name="minimal")
    logger1 = AlphaLoopLogger(config1)
    await logger1.info("Minimal config message")
    await logger1.close()

    # Development configuration
    print("\n🔹 Development configuration:")
    config2 = LoggingConfig(
        app_name="development",
        log_level=LogLevel.DEBUG,
        console_config=ConsoleConfig(
            enabled=True, use_colors=True, show_timestamp=True, show_level=True
        ),
        include_caller_info=True,
        truncate_long_messages=True,
        max_message_length=100,
    )
    logger2 = AlphaLoopLogger(config2)
    await logger2.debug("Development debug message")
    await logger2.info("Development info message")
    await logger2.close()

    # Production-like configuration
    print("\n🔹 Production-like configuration:")
    with tempfile.TemporaryDirectory() as temp_dir:
        config3 = LoggingConfig(
            app_name="production",
            log_level=LogLevel.WARNING,
            hostname="prod-server-01",
            file_config=FileConfig(
                logs_path=temp_dir,
                max_file_size=10 * 1024 * 1024,
                backup_count=10,
                rotation_enabled=True,
            ),
            console_config=ConsoleConfig(
                enabled=False  # Typically disabled in production
            ),
            include_caller_info=False,  # Less overhead
            truncate_long_messages=True,
        )
        logger3 = AlphaLoopLogger(config3)
        await logger3.info("This won't be logged (below WARNING level)")
        await logger3.warning("Production warning message")
        await logger3.error("Production error message")
        await logger3.close()

    print("✅ Configuration options demo completed\n")


async def main():
    """Run all logging demos."""
    print("🚀 AlphaLoop Logging Package Demo")
    print("=" * 60)
    print()

    try:
        await demo_basic_logging()
        await demo_file_logging()
        await demo_structured_logging()
        await demo_legacy_compatibility()
        await demo_telegram_simulation()
        await demo_error_resilience()
        await demo_configuration_options()

        print("🎉 All logging demos completed successfully!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
