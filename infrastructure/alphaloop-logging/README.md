# AlphaLoop Logging Package

A comprehensive, asynchronous logging package for AlphaLoop Core with multi-handler support, Telegram integration, structured logging, and modern Python best practices.

## Features

- **🔄 Asynchronous Logging**: Non-blocking async/await support
- **📁 File Logging**: Automatic file rotation with configurable size limits
- **💬 Telegram Integration**: Send critical logs directly to Telegram chats
- **🎨 Console Logging**: Rich console output with colors and emojis
- **⚙️ Structured Logging**: JSON-compatible structured log records
- **🔧 Flexible Configuration**: Environment-based or programmatic configuration
- **🛡️ Error Resilience**: Robust error handling to prevent logging failures
- **📊 Multiple Handlers**: Simultaneous logging to multiple destinations
- **🔗 Legacy Compatibility**: Drop-in replacement for legacy Logger class

## Installation

```bash
# From the infrastructure directory
cd infrastructure/alphaloop-logging
poetry install
```

## Quick Start

### Basic Usage

```python
import asyncio
from alphaloop_logging import AlphaLoopLogger, LoggingConfig

async def main():
    # Create configuration
    config = LoggingConfig.from_env("my-app")

    # Create logger
    logger = AlphaLoopLogger(config)

    # Log messages
    await logger.info("Application started", info="startup")
    await logger.warning("This is a warning message")
    await logger.error("Something went wrong", telegram=True)

    # Clean up
    await logger.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Configuration

```python
from alphaloop_logging import (
    AlphaLoopLogger,
    LoggingConfig,
    FileConfig,
    TelegramConfig,
    ConsoleConfig,
    LogLevel
)

# Create detailed configuration
config = LoggingConfig(
    app_name="alphaloop-service",
    log_level=LogLevel.DEBUG,
    hostname="rpi-node-01",

    # File logging with rotation
    file_config=FileConfig(
        logs_path="./logs",
        max_file_size=10 * 1024 * 1024,  # 10MB
        backup_count=5,
        rotation_enabled=True
    ),

    # Telegram notifications
    telegram_config=TelegramConfig(
        bot_token="your-bot-token",
        chat_id=-1001234567890,
        send_on_error=True,
        send_on_warning=True,
        send_on_critical=True
    ),

    # Console output
    console_config=ConsoleConfig(
        enabled=True,
        use_colors=True,
        show_timestamp=True
    )
)

logger = AlphaLoopLogger(config)
```

### Environment Configuration

Set environment variables:

```bash
export LOGS_PATH="./logs"
export LOG_LEVEL="INFO"
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_LOG_CHAT_ID="-1001234567890"
export TELEGRAM_LOGGING_ENABLED="true"
export HOSTNAME="rpi-node-01"
```

Then use:

```python
config = LoggingConfig.from_env("my-app")
logger = AlphaLoopLogger(config)
```

## API Reference

### AlphaLoopLogger

Main logger class with async support.

**Methods:**
- `async debug(message, info="", telegram=None, **extra)`: Log debug message
- `async info(message, info="", telegram=None, **extra)`: Log info message
- `async warning(message, info="", telegram=None, **extra)`: Log warning message
- `async error(message, info="", telegram=None, **extra)`: Log error message
- `async critical(message, info="", telegram=None, **extra)`: Log critical message
- `async launch(name)`: Log application launch (legacy compatibility)
- `async log(message, level="INFO", info="", telegram=None, **extra)`: Generic log method
- `async close()`: Close all handlers and cleanup

**Legacy Compatibility:**
```python
# Legacy-style usage (compatible with old Logger)
await logger("Error message", info="context", level="E", telegram=True)
```

### Configuration Classes

#### LoggingConfig

Main configuration class.

**Parameters:**
- `app_name`: Application name (required)
- `log_level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `hostname`: Hostname to include in logs
- `file_config`: File logging configuration
- `telegram_config`: Telegram integration configuration
- `console_config`: Console output configuration
- `include_caller_info`: Include caller function information
- `truncate_long_messages`: Truncate messages if too long
- `max_message_length`: Maximum message length

#### FileConfig

File logging configuration.

**Parameters:**
- `logs_path`: Directory for log files
- `enabled`: Enable/disable file logging
- `max_file_size`: Maximum file size before rotation (bytes)
- `backup_count`: Number of backup files to keep
- `rotation_enabled`: Enable file rotation

#### TelegramConfig

Telegram integration configuration.

**Parameters:**
- `bot_token`: Telegram bot token
- `chat_id`: Telegram chat/group ID
- `enabled`: Enable/disable Telegram logging
- `max_message_length`: Maximum message length for Telegram
- `send_on_error`: Send ERROR level messages
- `send_on_warning`: Send WARNING level messages
- `send_on_critical`: Send CRITICAL level messages
- `send_on_info`: Send INFO level messages
- `send_on_debug`: Send DEBUG level messages

#### ConsoleConfig

Console output configuration.

**Parameters:**
- `enabled`: Enable/disable console output
- `use_colors`: Use colors and emojis in output
- `show_timestamp`: Show timestamp in output
- `show_level`: Show log level in output

## Handlers

The logging system uses multiple handlers that can work simultaneously:

### FileHandler

- **Automatic Rotation**: Rotates files when they exceed size limit
- **Backup Management**: Keeps configurable number of backup files
- **Async I/O**: Non-blocking file operations
- **Thread-Safe**: Safe for concurrent access

### TelegramHandler

- **HTML Formatting**: Rich HTML messages with emojis
- **Rate Limiting**: Prevents API rate limit issues
- **Selective Sending**: Configure which levels to send
- **Error Resilience**: Never blocks main application

### ConsoleHandler

- **Rich Output**: Colors, emojis, and structured formatting
- **Configurable Display**: Control timestamp, level visibility
- **Performance**: Minimal overhead for console output

## Formatters

Each handler uses specialized formatters:

### TelegramFormatter

```
🚨 ERROR 🚨
💻 RPI-NODE-01
⏰ 2024-01-01 12:00:00 (UTC)

📂 Log File:
my-app_20240101_120000.log

🏷️ App:
my-application

⚙️ Context:
database_connection

📄 Message:
Failed to connect to database
```

### FileFormatter

```
2024-01-01 12:00:00 -> ERROR [my-app] (database_connection) Failed to connect to database
```

### ConsoleFormatter

```
[12:00:00] 🚨 ERROR [my-app] (database_connection) -> Failed to connect to database
```

## Advanced Features

### Structured Logging

Add structured data to log records:

```python
await logger.info(
    "User login successful",
    info="authentication",
    user_id="12345",
    ip_address="192.168.1.100",
    login_method="password"
)
```

### Telegram Override

Control Telegram sending per message:

```python
# Force send to Telegram regardless of level configuration
await logger.info("Important info", telegram=True)

# Prevent sending to Telegram
await logger.error("Local error", telegram=False)
```

### Caller Information

Automatically captures calling function information:

```python
# Logs will include function name, module, and line number
await logger.error("Something failed")
# Output: ... (my_module.my_function:42) Something failed
```

### Legacy Compatibility

Drop-in replacement for legacy Logger:

```python
# Old style
Log = Logger(app="my-app", debug_level="ON", logs_path="./logs")
Log("Error occurred", info="context", level="E")

# New style (async)
config = LoggingConfig.from_env("my-app")
logger = AlphaLoopLogger(config)
await logger("Error occurred", info="context", level="E")
```

## Error Handling

The logging system is designed to be resilient:

- **Handler Isolation**: Errors in one handler don't affect others
- **Graceful Degradation**: Continues working even if some handlers fail
- **No Recursion**: Logging errors don't cause infinite recursion
- **Silent Failures**: Handler errors are silently ignored to avoid disrupting main application

## Performance

- **Async I/O**: Non-blocking operations for file and network I/O
- **Concurrent Handlers**: All handlers process messages simultaneously
- **Rate Limiting**: Telegram handler includes built-in rate limiting
- **Efficient Rotation**: File rotation uses efficient file operations

## Best Practices

### 1. Use Appropriate Log Levels

```python
await logger.debug("Detailed debug information")
await logger.info("General information")
await logger.warning("Something unexpected happened")
await logger.error("An error occurred but application continues")
await logger.critical("Critical error - application may stop")
```

### 2. Provide Context

```python
await logger.error(
    "Database connection failed",
    info="database_manager",
    host="localhost",
    port=5432,
    retry_count=3
)
```

### 3. Use Telegram Wisely

```python
# Good: Critical errors that need immediate attention
await logger.critical("Service down", telegram=True)

# Good: Prevent spam for known issues
await logger.error("Expected error during maintenance", telegram=False)
```

### 4. Clean Up Resources

```python
try:
    # Your application code
    await logger.info("Application running")
finally:
    # Always clean up
    await logger.close()
```

### 5. Environment-Based Configuration

```python
# Development
config = LoggingConfig.from_env("my-app")
config.log_level = LogLevel.DEBUG
config.console_config.use_colors = True

# Production
config = LoggingConfig.from_env("my-app")
config.log_level = LogLevel.WARNING
config.telegram_config.send_on_info = False
```

## Migration from Legacy Logger

### Old Code

```python
from cryptobot_core.utils import Logger

Log = Logger(
    app="my-app.py",
    debug_level="ON",
    logs_path="./logs",
    console=True
)

Log("Error message", info="context", level="E", telegram=True)
Log.launch("My Application")
```

### New Code

```python
from alphaloop_logging import AlphaLoopLogger, LoggingConfig
import asyncio

async def main():
    config = LoggingConfig.from_env("my-app")
    logger = AlphaLoopLogger(config)

    await logger("Error message", info="context", level="E", telegram=True)
    await logger.launch("My Application")

    await logger.close()

asyncio.run(main())
```

## Development

```bash
# Install development dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Run linting
poetry run ruff check .

# Run type checking
poetry run mypy src/
```

## License

This package is part of the AlphaLoop Core project.
