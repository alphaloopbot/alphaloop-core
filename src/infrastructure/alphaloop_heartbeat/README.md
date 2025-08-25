# AlphaLoop Heartbeat Module

A health monitoring system for AlphaLoop services, providing heartbeat generation, health checks, and process monitoring capabilities.

## 💓 Overview

The AlphaLoop Heartbeat module provides a comprehensive health monitoring solution for all AlphaLoop services. It modernizes health monitoring with:

- **Heartbeat Generation** - File-based heartbeat signals
- **Health Checking** - Process and service health validation
- **Stale Detection** - Automatic detection of stale heartbeats
- **Process Monitoring** - Validate running processes
- **Integration Ready** - Works with all alphaloop-core services

## 🚀 Features

- ✅ **Heartbeat Generation** - File-based health signals
- ✅ **Health Checking** - Process and service validation
- ✅ **Stale Detection** - Automatic stale heartbeat detection
- ✅ **Process Monitoring** - Validate running processes
- ✅ **Async Support** - Non-blocking operations
- ✅ **Type Safety** - Full type hints

## 🔧 Usage

### **Importing the Module**

```python
# This is an internal module - no installation needed
from alphaloop_heartbeat import HeartbeatGenerator, HeartbeatChecker
```

### **Basic Usage**

```python
from alphaloop_heartbeat import HeartbeatGenerator, HeartbeatChecker

# Generate heartbeats
import asyncio
heartbeat_gen = HeartbeatGenerator("my-service")
asyncio.run(heartbeat_gen.generate_heartbeat())

# Check health
checker = HeartbeatChecker("my-service")
is_healthy = checker.is_healthy()
print(f"Service healthy: {is_healthy}")
```

### **Using in Services**

```python
# Example: System Metrics Service
from alphaloop_heartbeat import HeartbeatGenerator

class SystemMetricsService:
    def __init__(self):
        # Initialize heartbeat
        self.heartbeat_generator = HeartbeatGenerator("system-metrics")

    def collect_metrics(self):
        # Generate heartbeat before collecting
        asyncio.run(self.heartbeat_generator.generate_heartbeat())

        # ... metrics collection logic
        print("Metrics collected")
```

### **Health Checking**

```python
from alphaloop_heartbeat import HeartbeatChecker

# Check if service is healthy
checker = HeartbeatChecker("system-metrics")
if checker.is_healthy():
    print("Service is running normally")
else:
    print("Service may be down or stale")
```

## ⚙️ Configuration

### **Environment Variables**

```bash
# Heartbeat Configuration
HEARTBEAT_INTERVAL=30
HEARTBEAT_TIMEOUT=120
HEARTBEAT_DIRECTORY=/var/heartbeats
HEARTBEAT_STALE_THRESHOLD=60
```

### **Configuration from Environment**

```python
from alphaloop_heartbeat import HeartbeatSettings

# Load from environment
settings = HeartbeatSettings.from_env()
print(f"Heartbeat interval: {settings.interval}s")
```

## 🧪 Testing

```bash
# Test this module
cd src/infrastructure/alphaloop-heartbeat
python -m pytest tests/

# Test integration with alphaloop-core
make test-core
```

## 📚 API Reference

### **HeartbeatGenerator**

**Methods:**
- `generate_heartbeat()`: Generate a new heartbeat signal
- `get_heartbeat_file()`: Get the heartbeat file path

### **HeartbeatChecker**

**Methods:**
- `is_healthy()`: Check if service is healthy
- `is_stale()`: Check if heartbeat is stale
- `get_last_heartbeat()`: Get last heartbeat timestamp

### **HeartbeatSettings**

**Methods:**
- `from_env()`: Create settings from environment variables
- `validate()`: Validate configuration settings

## 🎯 Key Points

- **Internal module** - part of alphaloop-core
- **No installation needed** - direct import
- **No versioning** - evolves with alphaloop-core
- **Used by all services** - system-metrics, market-data, etc.

---

**🎯 Goal**: This heartbeat module provides a solid foundation for health monitoring across all alphaloop-core services.
