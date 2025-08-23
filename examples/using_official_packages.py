#!/usr/bin/env python3
"""
Example: Using Official AlphaLoop Infrastructure Packages in Core

This example demonstrates how alphaloop-core should use the official infrastructure packages
instead of implementing functionality directly.
"""

import asyncio

from alphaloop_core import get_all_package_configs, service_factory


async def example_using_official_packages():
    """Example of using official infrastructure packages in alphaloop-core."""

    print("🚀 AlphaLoop Core - Using Official Infrastructure Packages")
    print("=" * 50)

    # 1. Get all package configurations
    print("\n📋 Package Configurations:")
    configs = get_all_package_configs()
    for package_name, config in configs.items():
        print(f"  ✅ {package_name}: {type(config).__name__}")

    # 2. Use logging package
    print("\n📝 Using alphaloop-logging:")
    logger = await service_factory.get_logger()
    await logger.info("Core application started")
    await logger.warning("This is a test warning")

    # 3. Use cache package
    print("\n🗄️ Using alphaloop-cache:")
    cache_manager = await service_factory.get_cache_manager()
    _price_cache = await service_factory.get_price_cache()

    # Test cache connection
    try:
        is_connected = await cache_manager.test_connection()
        print(f"  ✅ Cache connected: {is_connected}")
    except Exception as e:
        print(f"  ⚠️ Cache connection failed (expected without Redis): {e}")

    # 4. Use storage package
    print("\n💾 Using alphaloop-storage:")
    database_manager = await service_factory.get_database_manager()
    _schema_manager = await service_factory.get_schema_manager()

    print(f"  ✅ Database config: {database_manager.config.host}:{database_manager.config.port}")
    print("  ✅ Schema manager ready")

    # 5. Use heartbeat package
    print("\n💓 Using alphaloop-heartbeat:")
    heartbeat_generator = await service_factory.get_heartbeat_generator()
    heartbeat_checker = await service_factory.get_heartbeat_checker()

    print(f"  ✅ Heartbeat generator: {type(heartbeat_generator).__name__}")
    print(f"  ✅ Heartbeat checker: {type(heartbeat_checker).__name__}")

    # 6. Use security package
    print("\n🔒 Using alphaloop-security:")
    authenticator = service_factory.get_authenticator()
    encryptor = service_factory.get_encryptor()
    url_composer = service_factory.get_secure_url_composer()

    print(f"  ✅ Authenticator: {type(authenticator).__name__}")
    print(f"  ✅ Encryptor: {type(encryptor).__name__}")
    print(f"  ✅ URL Composer: {type(url_composer).__name__}")

    # 7. Use pub/sub package
    print("\n📡 Using alphaloop-cache pub/sub:")
    pubsub_manager = await service_factory.get_pubsub_manager()

    print(f"  ✅ Pub/Sub manager: {type(pubsub_manager).__name__}")

    # 8. Use table handler (simplified)
    print("\n📊 Using alphaloop-storage table handler:")
    try:
        table_handler = await service_factory.get_table_handler("test_table")
        print(f"  ✅ Table handler: {type(table_handler).__name__}")
    except Exception as e:
        print(f"  ⚠️ Table handler failed (expected without schema): {type(e).__name__}")

    # 9. Cleanup
    print("\n🧹 Cleaning up:")
    await service_factory.close_all()
    print("  ✅ All services closed")

    print("\n🎉 Example completed successfully!")
    print("✅ alphaloop-core is now properly using official infrastructure packages!")


async def example_direct_package_usage():
    """Example of using infrastructure packages directly (alternative approach)."""

    print("\n🔄 Alternative: Direct Package Usage")
    print("=" * 40)

    # Direct imports from infrastructure packages
    from alphaloop_cache import CacheConfig, CacheManager
    from alphaloop_logging import AlphaLoopLogger, LoggingConfig
    from alphaloop_storage import DatabaseConfig, DatabaseManager

    # Create configurations
    cache_config = CacheConfig.from_env(prefix="CACHE_")
    logging_config = LoggingConfig.from_env(app_name="alphaloop-core")
    storage_config = DatabaseConfig.from_env(prefix="DATABASE_")

    print(f"  ✅ Cache config: {cache_config.host}:{cache_config.port}")
    print(f"  ✅ Logging config: {logging_config.log_level}")
    print(f"  ✅ Storage config: {storage_config.host}:{storage_config.port}")

    # Create managers
    cache_manager = CacheManager(cache_config)
    logger = AlphaLoopLogger(logging_config)
    database_manager = DatabaseManager(storage_config)

    print(f"  ✅ Cache manager: {type(cache_manager).__name__}")
    print(f"  ✅ Logger: {type(logger).__name__}")
    print(f"  ✅ Database manager: {type(database_manager).__name__}")

    # Cleanup
    await cache_manager.close()
    await logger.close()
    await database_manager.close()

    print("  ✅ Direct usage completed")


async def main():
    """Run all examples."""
    try:
        await example_using_official_packages()
        await example_direct_package_usage()

        print("\n" + "=" * 60)
        print("🎯 Key Benefits of Using Official Infrastructure Packages:")
        print("  ✅ No code duplication")
        print("  ✅ Consistent APIs across the system")
        print("  ✅ Centralized configuration management")
        print("  ✅ Easy testing and mocking")
        print("  ✅ Better maintainability")
        print("  ✅ Version control and updates")

    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
