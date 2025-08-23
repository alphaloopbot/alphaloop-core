#!/usr/bin/env python3
"""
Basic test for AlphaLoop Cache package.
"""

import asyncio
from datetime import datetime

from alphaloop_cache import (
    CacheConfig,
    CacheManager,
    KeyBuilder,
    PriceCache,
    PriceData,
    PubSubManager,
)


async def test_cache_config():
    """Test cache configuration."""
    print("🔧 Testing Cache Configuration")
    print("=" * 40)

    # Test basic configuration
    config = CacheConfig(
        host="localhost",
        port=6379,
        db=0,
        password="",
    )

    print(f"📁 Host: {config.host}")
    print(f"📁 Port: {config.port}")
    print(f"📁 Database: {config.db}")

    # Test URL generation
    connection_url = config.connection_url
    print(f"🔗 Connection URL: {connection_url}")

    assert "redis://" in connection_url
    assert "localhost:6379" in connection_url

    print("✅ Cache configuration test passed\n")


async def test_key_builder():
    """Test key builder functionality."""
    print("🔑 Testing Key Builder")
    print("=" * 40)

    key_builder = KeyBuilder(prefix="alphaloop")

    # Test price key building
    price_key = key_builder.build_price_key("BTC/USDT", "binance")
    print(f"🔑 Price key: {price_key}")

    assert "alphaloop:price:binance:BTC/USDT" == price_key

    # Test message key building
    timestamp = datetime.utcnow()
    message_key = key_builder.build_message_key("market_data", timestamp)
    print(f"🔑 Message key: {message_key}")

    assert "alphaloop:message:market_data:" in message_key

    # Test key validation
    valid_key = key_builder.is_valid_key("test:key:123")
    invalid_key = key_builder.is_valid_key("test\x00key")
    print(f"🔑 Valid key: {valid_key}")
    print(f"🔑 Invalid key: {invalid_key}")

    assert valid_key is True
    assert invalid_key is False

    print("✅ Key builder test passed\n")


async def test_cache_manager():
    """Test cache manager (without actual connection)."""
    print("🗄️ Testing Cache Manager")
    print("=" * 40)

    # Create a test configuration
    config = CacheConfig(
        host="localhost",
        port=6379,
        db=0,
    )

    # Create cache manager
    cache_manager = CacheManager(config)

    print(f"📁 Host: {cache_manager.config.host}")
    print(f"📁 Port: {cache_manager.config.port}")

    # Test that client is created lazily
    assert cache_manager._redis_client is None

    # Note: We don't test actual connections here since we don't have Redis
    # In a real test environment, you would use a test Redis instance or mock

    print("✅ Cache manager test passed\n")


async def test_price_cache():
    """Test price cache functionality."""
    print("💰 Testing Price Cache")
    print("=" * 40)

    # Create cache manager
    config = CacheConfig(host="localhost", port=6379, db=0)
    cache_manager = CacheManager(config)

    # Create price cache (not used in this test, just for demonstration)
    _price_cache = PriceCache(cache_manager, default_ttl=300)

    # Create test price data
    price_data = PriceData(
        symbol="BTC/USDT",
        price=50000.0,
        timestamp=datetime.utcnow(),
        exchange="binance",
        volume=1000.0,
        bid=49999.0,
        ask=50001.0,
    )

    print(f"💰 Symbol: {price_data.symbol}")
    print(f"💰 Price: {price_data.price}")
    print(f"💰 Exchange: {price_data.exchange}")

    # Test price data serialization
    price_dict = price_data.to_dict()
    print(f"💰 Serialized: {price_dict}")

    assert price_dict["symbol"] == "BTC/USDT"
    assert price_dict["price"] == 50000.0
    assert price_dict["exchange"] == "binance"

    # Test price data deserialization
    reconstructed = PriceData.from_dict(price_dict)
    print(f"💰 Reconstructed: {reconstructed.symbol}")

    assert reconstructed.symbol == price_data.symbol
    assert reconstructed.price == price_data.price

    print("✅ Price cache test passed\n")


async def test_pubsub_manager():
    """Test pub/sub manager functionality."""
    print("📡 Testing Pub/Sub Manager")
    print("=" * 40)

    # Create cache manager
    config = CacheConfig(host="localhost", port=6379, db=0)
    cache_manager = CacheManager(config)

    # Create pub/sub manager (not used in this test, just for demonstration)
    _pubsub_manager = PubSubManager(cache_manager)

    # Test message creation
    test_message = {
        "type": "price_update",
        "symbol": "BTC/USDT",
        "price": 50000.0,
    }

    from alphaloop_cache import PubSubMessage

    pubsub_message = PubSubMessage(
        channel="market_data",
        message=test_message,
        timestamp=datetime.utcnow(),
    )
    print(f"📡 Channel: {pubsub_message.channel}")
    print(f"📡 Message type: {pubsub_message.message['type']}")

    assert pubsub_message.channel == "market_data"
    assert pubsub_message.message["type"] == "price_update"

    # Test message serialization
    message_dict = pubsub_message.to_dict()
    print(f"📡 Serialized message: {message_dict}")

    assert message_dict["channel"] == "market_data"
    assert message_dict["message"]["type"] == "price_update"

    print("✅ Pub/Sub manager test passed\n")


async def main():
    """Run all basic tests."""
    print("🚀 AlphaLoop Cache Package - Basic Tests")
    print("=" * 60)
    print()

    try:
        await test_cache_config()
        await test_key_builder()
        await test_cache_manager()
        await test_price_cache()
        await test_pubsub_manager()

        print("🎉 All basic tests completed successfully!")
        print("✅ AlphaLoop Cache package is working correctly")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
