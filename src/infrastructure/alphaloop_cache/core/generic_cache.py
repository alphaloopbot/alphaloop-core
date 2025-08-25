"""Generic caching functionality for AlphaLoop Cache."""

from datetime import datetime, timedelta
from typing import Any

from ..exceptions import CacheError
from ..models.cache_entry import CacheEntry
from ..utils.key_builder import KeyBuilder
from .connection import CacheManager


class GenericCache:
    """Generic caching for any data type."""

    def __init__(
        self,
        cache_manager: CacheManager,
        default_ttl: int = 300,  # 5 minutes
        max_cache_size: int = 10000,
        prefix: str = "cache",
    ) -> None:
        """Initialize generic cache."""
        self.cache_manager = cache_manager
        self.default_ttl = default_ttl
        self.max_cache_size = max_cache_size
        self.key_builder = KeyBuilder(prefix=prefix)

    async def set_data(self, key: str, data: Any, ttl: int | None = None) -> bool:
        """Cache any data."""
        try:
            # Add cache metadata
            cache_entry = CacheEntry(
                key=key,
                data=data,
                timestamp=datetime.utcnow(),
                ttl=ttl or self.default_ttl,
            )

            success = await self.cache_manager.set_key(
                key, cache_entry.to_dict(), ttl or self.default_ttl
            )

            if success:
                # Also write a history entry with a time-suffixed key for retrieval by pattern
                history_key = f"{key}:{int(cache_entry.timestamp.timestamp())}"
                await self.cache_manager.set_key(
                    history_key, cache_entry.to_dict(), ttl or self.default_ttl
                )

            return success
        except Exception as e:
            raise CacheError(f"Failed to cache data for key {key}: {e}") from e

    async def get_data(self, key: str) -> Any | None:
        """Get cached data."""
        try:
            cached_data = await self.cache_manager.get_key(key)

            if cached_data is None:
                return None

            # Parse cache entry
            cache_entry = CacheEntry.from_dict(cached_data)

            # Check if expired
            if cache_entry.is_expired():
                await self.cache_manager.delete_key(key)
                return None

            # Return the actual data
            return cache_entry.data
        except Exception as e:
            raise CacheError(f"Failed to get data for key {key}: {e}") from e

    async def get_multiple(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple cached data items."""
        try:
            result = {}
            for key in keys:
                data = await self.get_data(key)
                if data is not None:
                    result[key] = data
            return result
        except Exception as e:
            raise CacheError(f"Failed to get multiple data items: {e}") from e

    async def get_history(self, key_pattern: str, hours: int = 24) -> list[dict[str, Any]]:
        """Get data history for a key pattern."""
        try:
            keys = await self._get_keys_by_pattern(key_pattern)

            history = []
            for key in keys:
                cached_data = await self.cache_manager.get_key(key)
                if cached_data:
                    cache_entry = CacheEntry.from_dict(cached_data)
                    if not cache_entry.is_expired():
                        # Filter by time range
                        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                        if cache_entry.timestamp >= cutoff_time:
                            history.append(
                                {
                                    "key": key,
                                    "data": cache_entry.data,
                                    "timestamp": cache_entry.timestamp,
                                }
                            )

            # Sort by timestamp
            history.sort(key=lambda x: x["timestamp"])
            return history
        except Exception as e:
            raise CacheError(f"Failed to get history for pattern {key_pattern}: {e}") from e

    async def delete_data(self, key: str) -> bool:
        """Delete cached data."""
        try:
            return await self.cache_manager.delete_key(key)
        except Exception as e:
            raise CacheError(f"Failed to delete data for key {key}: {e}") from e

    async def delete_by_pattern(self, pattern: str) -> int:
        """Delete all data matching a pattern."""
        try:
            keys = await self._get_keys_by_pattern(pattern)

            deleted_count = 0
            for key in keys:
                if await self.cache_manager.delete_key(key):
                    deleted_count += 1

            return deleted_count
        except Exception as e:
            raise CacheError(f"Failed to delete data by pattern {pattern}: {e}") from e

    async def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        try:
            total_keys = await self.cache_manager.get_keys_count()
            pattern_keys = await self.cache_manager.get_keys_count(f"{self.key_builder.prefix}:*")

            # Get memory usage
            memory_info = await self.cache_manager.get_memory_usage()

            return {
                "total_keys": total_keys,
                "pattern_keys": pattern_keys,
                "memory_usage": memory_info,
                "default_ttl": self.default_ttl,
                "max_cache_size": self.max_cache_size,
                "prefix": self.key_builder.prefix,
            }
        except Exception as e:
            raise CacheError(f"Failed to get cache stats: {e}") from e

    async def cleanup_expired(self) -> int:
        """Clean up expired cache entries."""
        try:
            pattern = f"{self.key_builder.prefix}:*"
            keys = await self._get_keys_by_pattern(pattern)

            cleaned_count = 0
            for key in keys:
                cached_data = await self.cache_manager.get_key(key)
                if cached_data:
                    cache_entry = CacheEntry.from_dict(cached_data)
                    if cache_entry.is_expired():
                        if await self.cache_manager.delete_key(key):
                            cleaned_count += 1

            return cleaned_count
        except Exception as e:
            raise CacheError(f"Failed to cleanup expired entries: {e}") from e

    async def _get_keys_by_pattern(self, pattern: str) -> list[str]:
        """Get keys matching pattern."""
        try:
            # Note: This is a simplified implementation
            # In production, you might want to use SCAN for large datasets
            keys = []
            cursor = 0
            while True:
                cursor, batch = await self.cache_manager.redis_client.scan(
                    cursor=cursor, match=pattern, count=100
                )
                keys.extend(batch)
                if cursor == 0:
                    break
            return keys
        except Exception as e:
            raise CacheError(f"Failed to get keys by pattern: {e}") from e
