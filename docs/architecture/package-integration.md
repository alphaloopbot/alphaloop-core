# Package Integration in AlphaLoop Core

## Overview

This document explains how `alphaloop-core` has been refactored to properly use the official AlphaLoop infrastructure packages instead of implementing functionality directly. This ensures clean architecture, avoids code duplication, and provides consistent APIs across the system.

## Before vs After

### ❌ **Before: Direct Dependencies**
```toml
# pyproject.toml - Direct dependencies
redis = "^5.0"           # Direct Redis implementation
cryptography = "^41.0.0" # Direct encryption implementation
structlog = "^23.2.0"    # Direct logging implementation
psutil = "^5.9"          # Direct system monitoring
```

### ✅ **After: Local Infrastructure Modules**
```toml
# pyproject.toml - Local, internal infrastructure modules
alphaloop_heartbeat = { path = "src/infrastructure/alphaloop_heartbeat" }
alphaloop_security  = { path = "src/infrastructure/alphaloop_security" }
alphaloop_logging   = { path = "src/infrastructure/alphaloop_logging" }
alphaloop_storage   = { path = "src/infrastructure/alphaloop_storage" }
alphaloop_cache     = { path = "src/infrastructure/alphaloop_cache" }
```

## Package Integration Architecture

### 1. **Centralized Configuration Management**

```python
# src/alphaloop_core/shared/utils/package_config.py
from alphaloop_cache import CacheConfig
from alphaloop_heartbeat import HeartbeatSettings
from alphaloop_logging import LoggingConfig
from alphaloop_storage import DatabaseConfig

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
```

### 2. **Service Factory Pattern**

```python
# src/alphaloop_core/shared/utils/service_factory.py
class ServiceFactory:
    """Factory for creating services using official AlphaLoop infrastructure packages."""

    async def get_cache_manager(self) -> CacheManager:
        """Get or create cache manager."""
        if self._cache_manager is None:
            config = get_cache_config()
            self._cache_manager = CacheManager(config)
        return self._cache_manager

    async def get_logger(self) -> AlphaLoopLogger:
        """Get or create logger."""
        if self._logger is None:
            config = get_logging_config()
            self._logger = AlphaLoopLogger(config)
        return self._logger

    async def get_heartbeat_generator(self, service_name: str = "alphaloop-core") -> HeartbeatGenerator:
        """Get or create heartbeat generator."""
        if self._heartbeat_generator is None:
            config = get_heartbeat_config()
            self._heartbeat_generator = HeartbeatGenerator(service_name, config)
        return self._heartbeat_generator
```

### 3. **Unified Exports**

```python
# src/alphaloop_core/__init__.py
from .shared.utils.service_factory import service_factory
from .shared.utils.package_config import (
    get_cache_config,
    get_heartbeat_config,
    get_logging_config,
    get_security_config,
    get_storage_config,
    get_all_package_configs,
)

__all__ = [
    "service_factory",
    "get_cache_config",
    "get_heartbeat_config",
    "get_logging_config",
    "get_security_config",
    "get_storage_config",
    "get_all_package_configs",
]
```

## Usage Examples

### **Option 1: Service Factory (Recommended)**

```python
from alphaloop_core import service_factory

# Get services through factory
logger = await service_factory.get_logger()
cache_manager = await service_factory.get_cache_manager()
heartbeat_generator = await service_factory.get_heartbeat_generator("my-service")

# Use services
logger.info("Application started")
cache_manager.set("test", "value")
await heartbeat_generator.generate_heartbeat()
```

### **Option 2: Direct Package Usage**

```python
from alphaloop_cache import CacheConfig, CacheManager
from alphaloop_logging import LoggingConfig, AlphaLoopLogger
from alphaloop_storage import DatabaseConfig, DatabaseManager

# Create configurations
cache_config = CacheConfig.from_env(prefix="CACHE_")
logging_config = LoggingConfig.from_env(app_name="alphaloop-core")
storage_config = DatabaseConfig.from_env(prefix="DATABASE_")

# Create managers
cache_manager = CacheManager(cache_config)
logger = AlphaLoopLogger(logging_config)
database_manager = DatabaseManager(storage_config)
```

### **Option 3: Configuration Access**

```python
from alphaloop_core import get_all_package_configs

# Get all configurations
configs = get_all_package_configs()
print(f"Cache config: {configs['cache']}")
print(f"Logging config: {configs['logging']}")
print(f"Storage config: {configs['storage']}")
```

## Package-Specific Integration

### **1. alphaloop-cache**
- **Purpose**: Redis/Valkey caching and pub/sub
- **Integration**: Cache management, price caching, message publishing
- **Configuration**: `CACHE_HOST`, `CACHE_PORT`, `CACHE_PASSWORD`

### **2. alphaloop-logging**
- **Purpose**: Structured logging with multiple handlers
- **Integration**: Application logging, error reporting, Telegram notifications
- **Configuration**: `LOG_LEVEL`, `TELEGRAM_BOT_TOKEN`, `LOGS_PATH`

### **3. alphaloop-security**
- **Purpose**: Encryption, authentication, secure URLs
- **Integration**: Data encryption, connection authentication, secure communication
- **Configuration**: `SECURITY_SECRET_KEY`, `SECURITY_ENCRYPTION_KEY`

### **4. alphaloop-storage**
- **Purpose**: Database management and schema handling
- **Integration**: Data persistence, table operations, schema management
- **Configuration**: `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`

### **5. alphaloop-heartbeat**
- **Purpose**: Health monitoring and service status
- **Integration**: Service health checks, monitoring, status reporting
- **Configuration**: `HEARTBEAT_INTERVAL`, `HEARTBEAT_DIRECTORY`

## Benefits of Package Integration

### **✅ Code Quality**
- **No Duplication**: Single implementation per functionality
- **Consistent APIs**: Uniform interfaces across the system
- **Better Testing**: Isolated, testable components
- **Type Safety**: Full type hints and validation

### **✅ Maintainability**
- **Centralized Updates**: Update infrastructure packages independently
- **Version Control**: Track package versions separately
- **Dependency Management**: Clear dependency boundaries
- **Documentation**: Package-specific documentation

### **✅ Architecture**
- **Clean Separation**: Clear boundaries between concerns
- **Modularity**: Independent, reusable components
- **Scalability**: Easy to extend and modify
- **Standards**: Consistent patterns across infrastructure packages

### **✅ Development Experience**
- **Easy Integration**: Simple service factory pattern
- **Configuration Management**: Centralized configuration
- **Error Handling**: Consistent error patterns
- **Debugging**: Clear component boundaries

## Migration Guide

### **For Existing Code**

1. **Replace Direct Imports**:
   ```python
   # Before
   import redis
   import structlog

   # After
   from alphaloop_core import service_factory
   ```

2. **Update Configuration**:
   ```python
   # Before
   redis_url = get_redis_url()

   # After
   cache_config = get_cache_config()
   ```

3. **Use Service Factory**:
   ```python
   # Before
   redis_client = redis.Redis.from_url(redis_url)

   # After
   cache_manager = await service_factory.get_cache_manager()
   ```

### **For New Code**

1. **Always use service factory for core services**
2. **Use package configurations for setup**
3. **Follow package-specific patterns**
4. **Leverage package documentation**

## Testing

### **Unit Testing**
```python
import pytest
from unittest.mock import patch
from alphaloop_core import service_factory

@pytest.mark.asyncio
async def test_cache_integration():
    with patch('alphaloop_core.shared.utils.service_factory.CacheManager', autospec=True) as MockCacheManager:
        cache_manager = await service_factory.get_cache_manager()
        MockCacheManager.assert_called_once()
        assert cache_manager is MockCacheManager.return_value
```

### **Integration Testing**
```python
import pytest
from alphaloop_core import service_factory

@pytest.mark.asyncio
async def test_full_integration():
    # Test all services work together
    logger = await service_factory.get_logger()
    cache_manager = await service_factory.get_cache_manager()

    await logger.info("Integration test")
    # Verify services interact correctly
```

## Environment Configuration

### **Required Environment Variables**

```bash
# Cache Configuration
CACHE_HOST=localhost
CACHE_PORT=6379
CACHE_PASSWORD=

# Logging Configuration
LOG_LEVEL=INFO
TELEGRAM_BOT_TOKEN=
LOGS_PATH=./logs

# Security Configuration
SECURITY_SECRET_KEY=your-secret-key
SECURITY_ENCRYPTION_KEY=your-encryption-key

# Storage Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=alphaloop

# Heartbeat Configuration
HEARTBEAT_INTERVAL=60
HEARTBEAT_DIRECTORY=./heartbeats
```

## Future Enhancements

### **Planned Improvements**
1. **Dependency Injection**: More sophisticated DI container
2. **Configuration Validation**: Enhanced validation rules
3. **Service Discovery**: Dynamic service registration
4. **Health Checks**: Integrated health monitoring
5. **Metrics**: Performance monitoring integration

### **Package Evolution**
1. **API Stability**: Maintain backward compatibility
2. **Feature Parity**: Ensure all legacy functionality is covered
3. **Performance**: Optimize package performance
4. **Documentation**: Comprehensive package documentation

## Conclusion

The refactoring of `alphaloop-core` to use official infrastructure packages represents a significant improvement in code quality, maintainability, and architecture. By leveraging the service factory pattern and centralized configuration management, the system now provides:

- **Clean separation of concerns**
- **Consistent APIs across infrastructure packages**
- **Easy testing and mocking**
- **Centralized configuration management**
- **Better error handling and debugging**

This approach ensures that `alphaloop-core` focuses on its core responsibilities while delegating specialized functionality to dedicated, well-tested infrastructure packages.
