# AlphaLoop Cache Infrastructure Module

A **generic** Redis/Valkey caching infrastructure module for AlphaLoop services, providing pure caching, pub/sub messaging, and data persistence capabilities without any business logic coupling.

## 🗄️ Overview

The AlphaLoop Cache infrastructure module provides **pure caching infrastructure** for all AlphaLoop services. It follows Clean Architecture principles by providing generic caching capabilities without any business logic coupling:

- **Redis/Valkey Integration** - High-performance caching backend
- **Pub/Sub Messaging** - Real-time message broadcasting
- **Data Persistence** - Configurable data persistence
- **Async Support** - Non-blocking operations
- **Integration Ready** - Works with all alphaloop-core services

## 🚀 Features

- ✅ **Generic Caching** - Pure infrastructure caching (no business logic)
- ✅ **Pub/Sub** - Real-time message broadcasting
- ✅ **Data Persistence** - Configurable persistence
- ✅ **Async Support** - Non-blocking operations
- ✅ **Type Safety** - Full type hints
- ✅ **Error Handling** - Comprehensive error management
- ✅ **Clean Architecture** - Infrastructure-only, no domain coupling

## 🔧 Usage

### **Importing the Module**

```python
# This is an internal module - no installation needed
from infrastructure.alphaloop_cache import CacheManager, GenericCache, PubSubManager
```

### **Basic Caching**

```python
from infrastructure.alphaloop_cache import CacheManager, GenericCache

# Create cache manager
cache_manager = CacheManager()

# Create generic cache with prefix
generic_cache = GenericCache(cache_manager, prefix="myapp", default_ttl=300)

# Set cache value
await generic_cache.set_data("user:123", {"name": "John", "email": "john@example.com"}, ttl=3600)

# Get cache value
user_data = await generic_cache.get_data("user:123")
print(f"User data: {user_data}")

# Check if key exists
exists = await cache_manager.exists("user:123")
print(f"Key exists: {exists}")
```

### **Pub/Sub Messaging**

```python
from infrastructure.alphaloop_cache import PubSubManager

# Create pub/sub manager
pubsub_manager = PubSubManager(cache_manager)

# Subscribe to channel
async def handle_message(message):
    print(f"Received: {message}")

await pubsub_manager.subscribe("market-data", handle_message)

# Publish message
await pubsub_manager.publish("market-data", {"symbol": "BTC/USDT", "price": 50000})
```

### **Using in Services**

```python
# Example: Market Data Service with Caching
from infrastructure.alphaloop_cache import CacheManager, GenericCache

class MarketDataService:
    def __init__(self):
        # Initialize cache
        self.cache_manager = CacheManager()
        self.generic_cache = GenericCache(self.cache_manager, prefix="market", default_ttl=300)

    async def get_latest_price(self, symbol):
        # Try cache first
        cache_key = f"price:{symbol}"
        cached_price = await self.generic_cache.get_data(cache_key)

        if cached_price:
            return cached_price

        # Fetch from exchange
        price = await self.fetch_from_exchange(symbol)

        # Cache for 5 minutes
        await self.generic_cache.set_data(cache_key, price, ttl=300)
        return price
```

### **Advanced Caching**

```python
from infrastructure.alphaloop_cache import CacheManager, GenericCache

cache_manager = CacheManager()
generic_cache = GenericCache(cache_manager, prefix="app")

# Set multiple values
await generic_cache.set_data("key1", "value1")
await generic_cache.set_data("key2", "value2")
await generic_cache.set_data("key3", "value3")

# Get multiple values
values = await generic_cache.get_multiple(["key1", "key2", "key3"])

# Delete keys
await generic_cache.delete_data("key1")
await generic_cache.delete_data("key2")

# Get cache statistics
stats = await generic_cache.get_cache_stats()
print(f"Cache stats: {stats}")
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
from infrastructure.alphaloop_cache import CacheConfig

# Load from environment
config = CacheConfig.from_env()
print(f"Cache host: {config.host}")
```

## 🧪 Testing

```bash
# Test this module
cd src/infrastructure/alphaloop_cache
python tests/test_cache_basic.py

# Test integration with alphaloop-core
make test-core
```

## 📚 API Reference

### **CacheManager**

**Methods:**
- `set_key(key, value, ttl)`: Set cache value with TTL
- `get_key(key)`: Get cache value
- `delete_key(key)`: Delete cache key
- `exists(key)`: Check if key exists
- `get_keys_count(pattern)`: Count keys matching pattern
- `get_memory_usage()`: Get Redis memory usage

### **GenericCache**

**Methods:**
- `set_data(key, data, ttl)`: Set any data with TTL
- `get_data(key)`: Get cached data
- `get_multiple(keys)`: Get multiple data items
- `get_history(pattern, hours)`: Get data history
- `delete_data(key)`: Delete cached data
- `delete_by_pattern(pattern)`: Delete by pattern
- `get_cache_stats()`: Get cache statistics
- `cleanup_expired()`: Clean up expired entries

### **PubSubManager**

**Methods:**
- `subscribe(channel, callback)`: Subscribe to channel
- `publish(channel, message)`: Publish message
- `unsubscribe(channel)`: Unsubscribe from channel
- `get_channel_messages(channel, limit)`: Get recent messages
- `close()`: Close pub/sub connection

### **CacheConfig**

**Methods:**
- `from_env()`: Create config from environment variables
- `validate()`: Validate configuration settings

## 🏗️ Architecture

### **Clean Architecture Compliance**

This module follows **Clean Architecture principles**:

- ✅ **Pure Infrastructure** - No business logic coupling
- ✅ **Generic Caching** - Can cache any data type
- ✅ **Domain Independence** - No market data, trading, or business concepts
- ✅ **Reusable** - Used by all services without modification

### **Business Logic Separation**

**Before (Coupled):**
```python
# ❌ Business logic in infrastructure
from alphaloop_cache import PriceCache, PriceData
price_cache = PriceCache(cache_manager)
price_data = PriceData(symbol="BTC/USDT", price=50000, exchange="binance")
```

**After (Decoupled):**
```python
# ✅ Pure infrastructure
from infrastructure.alphaloop_cache import GenericCache
generic_cache = GenericCache(cache_manager, prefix="price")

# ✅ Business logic in core
from alphaloop_core.services.cache import PriceCacheService
price_cache = PriceCacheService(cache_manager)
```

## 🎯 Key Points

- **Internal module** - part of alphaloop-core
- **No installation needed** - direct import
- **No versioning** - evolves with alphaloop-core
- **Used by all services** - system-metrics, market-data, etc.
- **Pure infrastructure** - no business logic coupling

---

**🎯 Goal**: This cache module provides a solid foundation for caching and messaging across all alphaloop-core services.
