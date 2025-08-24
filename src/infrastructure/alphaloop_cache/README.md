# AlphaLoop Cache Module

A Redis/Valkey caching system for AlphaLoop services, providing caching, pub/sub messaging, and data persistence capabilities.

## 🗄️ Overview

The AlphaLoop Cache module provides a comprehensive caching solution for all AlphaLoop services. It modernizes caching with:

- **Redis/Valkey Integration** - High-performance caching backend
- **Pub/Sub Messaging** - Real-time message broadcasting
- **Data Persistence** - Configurable data persistence
- **Async Support** - Non-blocking operations
- **Integration Ready** - Works with all alphaloop-core services

## 🚀 Features

- ✅ **Caching** - Key-value caching with TTL
- ✅ **Pub/Sub** - Real-time message broadcasting
- ✅ **Data Persistence** - Configurable persistence
- ✅ **Async Support** - Non-blocking operations
- ✅ **Type Safety** - Full type hints
- ✅ **Error Handling** - Comprehensive error management

## 🔧 Usage

### **Importing the Module**

```python
# This is an internal module - no installation needed
from alphaloop_cache import CacheManager, PubSubManager
```

### **Basic Caching**

```python
from alphaloop_cache import CacheManager

# Create cache manager
cache_manager = CacheManager()

# Set cache value
cache_manager.set("user:123", {"name": "John", "email": "john@example.com"}, ttl=3600)

# Get cache value
user_data = cache_manager.get("user:123")
print(f"User data: {user_data}")

# Check if key exists
exists = cache_manager.exists("user:123")
print(f"Key exists: {exists}")
```

### **Pub/Sub Messaging**

```python
from alphaloop_cache import PubSubManager

# Create pub/sub manager
pubsub_manager = PubSubManager()

# Subscribe to channel
async def handle_message(message):
    print(f"Received: {message}")

pubsub_manager.subscribe("market-data", handle_message)

# Publish message
pubsub_manager.publish("market-data", {"symbol": "BTC/USDT", "price": 50000})
```

### **Using in Services**

```python
# Example: Market Data Service with Caching
from alphaloop_cache import CacheManager

class MarketDataService:
    def __init__(self):
        # Initialize cache
        self.cache_manager = CacheManager()

    def get_latest_price(self, symbol):
        # Try cache first
        cache_key = f"price:{symbol}"
        cached_price = self.cache_manager.get(cache_key)

        if cached_price:
            return cached_price

        # Fetch from exchange
        price = self.fetch_from_exchange(symbol)

        # Cache for 5 minutes
        self.cache_manager.set(cache_key, price, ttl=300)
        return price
```

### **Advanced Caching**

```python
from alphaloop_cache import CacheManager

cache_manager = CacheManager()

# Set multiple values
cache_manager.mset({
    "key1": "value1",
    "key2": "value2",
    "key3": "value3"
})

# Get multiple values
values = cache_manager.mget(["key1", "key2", "key3"])

# Delete keys
cache_manager.delete("key1", "key2")

# Clear all cache
cache_manager.clear()
```

## ⚙️ Configuration

### **Environment Variables**

```bash
# Cache Configuration
CACHE_HOST=localhost
CACHE_PORT=6379
CACHE_DB=0
CACHE_PASSWORD=
CACHE_SSL=false
CACHE_MAX_CONNECTIONS=10
```

### **Configuration from Environment**

```python
from alphaloop_cache import CacheConfig

# Load from environment
config = CacheConfig.from_env()
print(f"Cache host: {config.host}")
```

## 🧪 Testing

```bash
# Test this module
cd src/infrastructure/alphaloop-cache
python -m pytest tests/

# Test integration with alphaloop-core
make test-core
```

## 📚 API Reference

### **CacheManager**

**Methods:**
- `set(key, value, ttl)`: Set cache value with TTL
- `get(key)`: Get cache value
- `delete(*keys)`: Delete cache keys
- `exists(key)`: Check if key exists
- `clear()`: Clear all cache
- `mset(mapping)`: Set multiple values
- `mget(keys)`: Get multiple values

### **PubSubManager**

**Methods:**
- `subscribe(channel, callback)`: Subscribe to channel
- `publish(channel, message)`: Publish message
- `unsubscribe(channel)`: Unsubscribe from channel
- `close()`: Close pub/sub connection

### **CacheConfig**

**Methods:**
- `from_env()`: Create config from environment variables
- `validate()`: Validate configuration settings

## 🎯 Key Points

- **Internal module** - part of alphaloop-core
- **No installation needed** - direct import
- **No versioning** - evolves with alphaloop-core
- **Used by all services** - system-metrics, market-data, etc.

---

**🎯 Goal**: This cache module provides a solid foundation for caching and messaging across all alphaloop-core services.
