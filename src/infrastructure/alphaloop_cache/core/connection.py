"""
Cache connection management for AlphaLoop Cache.

This module provides comprehensive cache connection management for the AlphaLoop
Cache system, supporting Redis/Valkey connections with connection pooling,
configuration management, and error handling.

The module includes configuration management, connection pooling, client
management, and utilities for cache operations with proper resource cleanup.

Key Features:
- Redis/Valkey connection management
- Connection pooling and configuration
- Configuration from environment variables
- SSL/TLS support
- Connection health monitoring
- Error handling and validation
- Async support
"""

from dataclasses import dataclass
import json
from typing import Any

import redis.asyncio as redis
from redis.asyncio import Redis

from infrastructure.alphaloop_cache.exceptions import CacheConnectionError, CacheOperationError


@dataclass
class CacheConfig:
    """
    Configuration for cache connections.

    This class encapsulates all configuration parameters needed for cache
    connections, including connection details, pooling settings, and security
    parameters. It provides validation and environment variable loading
    capabilities.

    The configuration supports both development and production environments
    with sensible defaults and comprehensive validation for Redis/Valkey
    connections.

    Key Features:
    - Connection parameter management
    - Environment variable loading
    - Configuration validation
    - SSL/TLS support
    - Connection pooling configuration
    - Timeout settings

    Usage:
        config = CacheConfig.from_env(prefix="CACHE_")
        config = CacheConfig(
            host="localhost",
            port=6379,
            db=0
        )
    """

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str = ""
    ssl: bool = False
    ssl_cert_reqs: str = "required"
    max_connections: int = 20
    retry_on_timeout: bool = True
    socket_connect_timeout: int = 5
    socket_timeout: int = 5
    decode_responses: bool = True
    encoding: str = "utf-8"

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.host:
            raise ValueError("Cache host is required")
        if self.port <= 0 or self.port > 65535:
            raise ValueError("Invalid port number")
        if self.db < 0 or self.db > 15:
            raise ValueError("Database number must be between 0 and 15")

    @property
    def connection_url(self) -> str:
        """Get Redis connection URL."""
        protocol = "rediss" if self.ssl else "redis"
        auth_part = f":{self.password}@" if self.password else ""
        return f"{protocol}://{auth_part}{self.host}:{self.port}/{self.db}"

    @classmethod
    def from_env(cls, prefix: str = "CACHE_") -> "CacheConfig":
        """Create configuration from environment variables."""
        import os

        return cls(
            host=os.getenv(f"{prefix}HOST", "localhost"),
            port=int(os.getenv(f"{prefix}PORT", "6379")),
            db=int(os.getenv(f"{prefix}DB", "0")),
            password=os.getenv(f"{prefix}PASSWORD", ""),
            ssl=os.getenv(f"{prefix}SSL", "false").lower() == "true",
            ssl_cert_reqs=os.getenv(f"{prefix}SSL_CERT_REQS", "required"),
            max_connections=int(os.getenv(f"{prefix}MAX_CONNECTIONS", "20")),
            retry_on_timeout=os.getenv(f"{prefix}RETRY_ON_TIMEOUT", "true").lower() == "true",
            socket_connect_timeout=int(os.getenv(f"{prefix}SOCKET_CONNECT_TIMEOUT", "5")),
            socket_timeout=int(os.getenv(f"{prefix}SOCKET_TIMEOUT", "5")),
            decode_responses=os.getenv(f"{prefix}DECODE_RESPONSES", "true").lower() == "true",
            encoding=os.getenv(f"{prefix}ENCODING", "utf-8"),
        )


class CacheManager:
    """Manages cache connections and operations."""

    def __init__(self, config: CacheConfig) -> None:
        """Initialize cache manager."""
        self.config = config
        self._redis_client: Redis | None = None
        self._connection_pool: redis.ConnectionPool | None = None

    @property
    def redis_client(self) -> Redis:
        """Get Redis client instance."""
        if self._redis_client is None:
            self._redis_client = self._create_redis_client()
        return self._redis_client

    def _create_redis_client(self) -> Redis:
        """Create Redis client with configuration."""
        try:
            # Create connection pool
            self._connection_pool = redis.ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password if self.config.password else None,
                ssl=self.config.ssl,
                ssl_cert_reqs=self.config.ssl_cert_reqs,
                max_connections=self.config.max_connections,
                retry_on_timeout=self.config.retry_on_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                socket_timeout=self.config.socket_timeout,
                decode_responses=self.config.decode_responses,
                encoding=self.config.encoding,
            )

            # Create Redis client
            return redis.Redis(connection_pool=self._connection_pool)
        except Exception as e:
            raise CacheConnectionError(f"Failed to create Redis client: {e}") from e

    async def test_connection(self) -> bool:
        """Test cache connection."""
        try:
            await self.redis_client.ping()
            return True
        except Exception as e:
            raise CacheConnectionError(f"Cache connection test failed: {e}") from e

    async def get_info(self) -> dict[str, Any]:
        """Get cache server information."""
        try:
            info = await self.redis_client.info()
            return {
                "server": info.get("server", {}),
                "clients": info.get("clients", {}),
                "memory": info.get("memory", {}),
                "stats": info.get("stats", {}),
                "keyspace": info.get("keyspace", {}),
            }
        except Exception as e:
            raise CacheOperationError(f"Failed to get cache info: {e}") from e

    async def get_memory_usage(self) -> dict[str, Any]:
        """Get memory usage information."""
        try:
            info = await self.redis_client.info("memory")
            return {
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "used_memory_peak": info.get("used_memory_peak", 0),
                "used_memory_peak_human": info.get("used_memory_peak_human", "0B"),
                "used_memory_rss": info.get("used_memory_rss", 0),
                "used_memory_rss_human": info.get("used_memory_rss_human", "0B"),
            }
        except Exception as e:
            raise CacheOperationError(f"Failed to get memory usage: {e}") from e

    async def get_keys_count(self, pattern: str = "*") -> int:
        """Get count of keys matching pattern (uses SCAN to avoid blocking)."""
        try:
            if pattern == "*":
                return await self.redis_client.dbsize()
            count = 0
            cursor = 0
            while True:
                cursor, keys = await self.redis_client.scan(
                    cursor=cursor, match=pattern, count=1000
                )
                count += len(keys)
                if cursor == 0:
                    break
            return count
        except Exception as e:
            raise CacheOperationError(f"Failed to get keys count (pattern={pattern}): {e}") from e

    async def flush_db(self) -> bool:
        """Flush current database."""
        try:
            await self.redis_client.flushdb()
            return True
        except Exception as e:
            raise CacheOperationError(f"Failed to flush database: {e}") from e

    async def set_key(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set key with optional TTL."""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            await self.redis_client.set(key, value, ex=ttl)
            return True
        except Exception as e:
            raise CacheOperationError(f"Failed to set key {key}: {e}") from e

    async def get_key(self, key: str) -> Any:
        """Get value for key."""
        try:
            value = await self.redis_client.get(key)
            if value is None:
                return None

            # Try to parse as JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            raise CacheOperationError(f"Failed to get key {key}: {e}") from e

    async def delete_key(self, key: str) -> bool:
        """Delete key."""
        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            raise CacheOperationError(f"Failed to delete key {key}: {e}") from e

    async def key_exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            result = await self.redis_client.exists(key)
            return result > 0
        except Exception as e:
            raise CacheOperationError(f"Failed to check key existence {key}: {e}") from e

    async def get_ttl(self, key: str) -> int:
        """Get TTL for key."""
        try:
            return await self.redis_client.ttl(key)
        except Exception as e:
            raise CacheOperationError(f"Failed to get TTL for key {key}: {e}") from e

    async def set_ttl(self, key: str, ttl: int) -> bool:
        """Set TTL for key."""
        try:
            return await self.redis_client.expire(key, ttl)
        except Exception as e:
            raise CacheOperationError(f"Failed to set TTL for key {key}: {e}") from e

    async def close(self) -> None:
        """Close cache connections."""
        if self._redis_client:
            await self._redis_client.close()
        if self._connection_pool:
            await self._connection_pool.disconnect()


# Convenience function for creating cache manager
def create_cache_manager(
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    password: str = "",
    **kwargs: Any,
) -> CacheManager:
    """Create a cache manager with the given configuration."""
    config = CacheConfig(
        host=host,
        port=port,
        db=db,
        password=password,
        **kwargs,
    )
    return CacheManager(config)
