# AlphaLoop Logging Module

A centralized logging system for AlphaLoop services, providing structured logging with multiple handlers, Telegram integration, and configurable output formats.

## 📝 Overview

The AlphaLoop Logging module provides a comprehensive logging solution for all AlphaLoop services. It modernizes logging with:

- **Multi-Handler Support** - Console, file, and Telegram handlers
- **Structured Logging** - JSON and text formats
- **Async Support** - Non-blocking logging operations
- **Environment Configuration** - Easy setup via environment variables
- **Integration Ready** - Works with all alphaloop-core services

## 🚀 Features

- ✅ **Multiple Handlers** - Console, file, Telegram
- ✅ **Structured Output** - JSON and text formats
- ✅ **Async Operations** - Non-blocking logging
- ✅ **Environment Config** - Easy configuration
- ✅ **Type Safety** - Full type hints
- ✅ **Error Handling** - Comprehensive error management

## 🔧 Usage

### **Importing the Module**

```python
# This is an internal module - no installation needed
from alphaloop_logging import AlphaLoopLogger, LoggingConfig
```

### **Basic Usage**

```python
from alphaloop_logging import AlphaLoopLogger, LoggingConfig

# Create logging configuration
config = LoggingConfig.from_env(app_name="my-service")

# Create logger
logger = AlphaLoopLogger(config)

# Use logger
logger.info("Service started successfully")
logger.error("An error occurred", extra={"error_code": 500})
```

### **Configuration from Environment**

```python
# Environment variables
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/alphaloop/app.log
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

# Load configuration
config = LoggingConfig.from_env(app_name="system-metrics")
logger = AlphaLoopLogger(config)
```

### **Using in Services**

```python
# Example: System Metrics Service
from alphaloop_logging import AlphaLoopLogger, LoggingConfig

class SystemMetricsService:
    def __init__(self):
        # Initialize logging
        logging_config = LoggingConfig.from_env(app_name="system-metrics")
        self.logger = AlphaLoopLogger(logging_config)

    def collect_metrics(self):
        self.logger.info("Collecting system metrics...")
        # ... metrics collection logic
        self.logger.info("Metrics collected successfully")
```

## ⚙️ Configuration

### **Environment Variables**

```bash
# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/alphaloop/app.log
LOG_MAX_SIZE=10MB
LOG_BACKUP_COUNT=5

# Telegram Integration
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_LOG_LEVEL=ERROR
```

### **Log Levels**

- `DEBUG` - Detailed information for debugging
- `INFO` - General information about program execution
- `WARNING` - Indicate a potential problem
- `ERROR` - A more serious problem
- `CRITICAL` - A critical problem that may prevent the program from running

## 🧪 Testing

```bash
# Test this module
cd src/infrastructure/alphaloop_logging
python -m pytest tests/

# Test integration with alphaloop-core
make test-core
```

## 📚 API Reference

### **LoggingConfig**

**Methods:**
- `from_env(app_name)`: Create config from environment variables
- `validate()`: Validate configuration settings

### **AlphaLoopLogger**

**Methods:**
- `debug(message, **kwargs)`: Log debug message
- `info(message, **kwargs)`: Log info message
- `warning(message, **kwargs)`: Log warning message
- `error(message, **kwargs)`: Log error message
- `critical(message, **kwargs)`: Log critical message

## 🎯 Key Points

- **Internal module** - part of alphaloop-core
- **No installation needed** - direct import
- **No versioning** - evolves with alphaloop-core
- **Used by all services** - system-metrics, market-data, etc.

---

**🎯 Goal**: This logging module provides a solid foundation for structured logging across all alphaloop-core services.
