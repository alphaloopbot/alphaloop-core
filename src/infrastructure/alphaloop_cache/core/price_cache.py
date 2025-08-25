"""Price caching functionality for AlphaLoop Cache."""

from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel

from ..exceptions import PriceCacheError
from ..models.cache_entry import CacheEntry
from ..utils.key_builder import KeyBuilder
from .connection import CacheManager


class PriceData(BaseModel):
    """Price data model."""

    symbol: str
    price: float
    timestamp: datetime
    exchange: str
    volume: float | None = None
    bid: float | None = None
    ask: float | None = None
    high_24h: float | None = None
    low_24h: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "symbol": self.symbol,
            "price": self.price,
            "timestamp": self.timestamp.isoformat(),
            "exchange": self.exchange,
            "volume": self.volume,
            "bid": self.bid,
            "ask": self.ask,
            "high_24h": self.high_24h,
            "low_24h": self.low_24h,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PriceData":
        """Create from dictionary."""
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class PriceCache:
    """Price caching for local instances and MockExchange."""

    def __init__(
        self,
        cache_manager: CacheManager,
        default_ttl: int = 300,  # 5 minutes
        max_cache_size: int = 10000,
    ) -> None:
        """Initialize price cache."""
        self.cache_manager = cache_manager
        self.default_ttl = default_ttl
        self.max_cache_size = max_cache_size
        self.key_builder = KeyBuilder(prefix="price")

    async def cache_price(self, price_data: PriceData, ttl: int | None = None) -> bool:
        """Cache price data."""
        try:
            key = self.key_builder.build_price_key(
                price_data.symbol, price_data.exchange
            )
            value = price_data.to_dict()

            # Add cache metadata
            cache_entry = CacheEntry(
                key=key,
                data=value,
                timestamp=datetime.utcnow(),
                ttl=ttl or self.default_ttl,
            )

            success = await self.cache_manager.set_key(
                key, cache_entry.to_dict(), ttl or self.default_ttl
            )

            if success:
                await self._update_price_index(price_data.symbol, price_data.exchange)
                # Also write a history entry with a time-suffixed key for retrieval by pattern
                history_key = f"{key}:{int(cache_entry.timestamp.timestamp())}"
                await self.cache_manager.set_key(
                    history_key, cache_entry.to_dict(), ttl or self.default_ttl
                )

            return success
        except Exception as e:
            raise PriceCacheError(
                f"Failed to cache price for {price_data.symbol}: {e}"
            ) from e

    async def get_price(self, symbol: str, exchange: str) -> PriceData | None:
        """Get cached price data."""
        try:
            key = self.key_builder.build_price_key(symbol, exchange)
            cached_data = await self.cache_manager.get_key(key)

            if cached_data is None:
                return None

            # Parse cache entry
            cache_entry = CacheEntry.from_dict(cached_data)

            # Check if expired
            if cache_entry.is_expired():
                await self.cache_manager.delete_key(key)
                return None

            # Parse price data
            return PriceData.from_dict(cache_entry.data)
        except Exception as e:
            raise PriceCacheError(f"Failed to get price for {symbol}: {e}") from e

    async def get_latest_prices(
        self, symbols: list[str], exchange: str
    ) -> dict[str, PriceData]:
        """Get latest prices for multiple symbols."""
        try:
            result = {}
            for symbol in symbols:
                price_data = await self.get_price(symbol, exchange)
                if price_data:
                    result[symbol] = price_data
            return result
        except Exception as e:
            raise PriceCacheError(f"Failed to get latest prices: {e}") from e

    async def get_price_history(
        self, symbol: str, exchange: str, hours: int = 24
    ) -> list[PriceData]:
        """Get price history for a symbol."""
        try:
            pattern = self.key_builder.build_price_history_pattern(symbol, exchange)
            keys = await self._get_keys_by_pattern(pattern)

            history = []
            for key in keys:
                cached_data = await self.cache_manager.get_key(key)
                if cached_data:
                    cache_entry = CacheEntry.from_dict(cached_data)
                    if not cache_entry.is_expired():
                        price_data = PriceData.from_dict(cache_entry.data)
                        # Filter by time range
                        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                        if price_data.timestamp >= cutoff_time:
                            history.append(price_data)

            # Sort by timestamp
            history.sort(key=lambda x: x.timestamp)
            return history
        except Exception as e:
            raise PriceCacheError(
                f"Failed to get price history for {symbol}: {e}"
            ) from e

    async def invalidate_price(self, symbol: str, exchange: str) -> bool:
        """Invalidate cached price."""
        try:
            key = self.key_builder.build_price_key(symbol, exchange)
            return await self.cache_manager.delete_key(key)
        except Exception as e:
            raise PriceCacheError(
                f"Failed to invalidate price for {symbol}: {e}"
            ) from e

    async def invalidate_exchange_prices(self, exchange: str) -> int:
        """Invalidate all prices for an exchange."""
        try:
            pattern = self.key_builder.build_exchange_pattern(exchange)
            keys = await self._get_keys_by_pattern(pattern)

            deleted_count = 0
            for key in keys:
                if await self.cache_manager.delete_key(key):
                    deleted_count += 1

            return deleted_count
        except Exception as e:
            raise PriceCacheError(f"Failed to invalidate exchange prices: {e}") from e

    async def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        try:
            total_keys = await self.cache_manager.get_keys_count()
            price_keys = await self.cache_manager.get_keys_count("price:*")

            # Get memory usage
            memory_info = await self.cache_manager.get_memory_usage()

            return {
                "total_keys": total_keys,
                "price_keys": price_keys,
                "memory_usage": memory_info,
                "default_ttl": self.default_ttl,
                "max_cache_size": self.max_cache_size,
            }
        except Exception as e:
            raise PriceCacheError(f"Failed to get cache stats: {e}") from e

    async def cleanup_expired(self) -> int:
        """Clean up expired cache entries."""
        try:
            # This is a simplified cleanup - in production, you might want
            # to use Redis TTL or implement a more sophisticated cleanup
            pattern = "price:*"
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
            raise PriceCacheError(f"Failed to cleanup expired entries: {e}") from e

    async def _update_price_index(self, symbol: str, exchange: str) -> None:
        """Update price index for quick lookups."""
        try:
            index_key = self.key_builder.build_index_key(symbol, exchange)
            timestamp = datetime.utcnow().isoformat()
            await self.cache_manager.set_key(index_key, timestamp, ttl=self.default_ttl)
        except Exception as e:
            # Log but don't fail the main operation
            print(f"Warning: Failed to update price index: {e}")

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
            raise PriceCacheError(f"Failed to get keys by pattern: {e}") from e

    async def get_mock_exchange_data(self, symbol: str) -> dict[str, Any] | None:
        """Get data suitable for MockExchange."""
        try:
            # Try to get from multiple exchanges
            exchanges = ["binance", "coinbase", "kraken"]

            for exchange in exchanges:
                price_data = await self.get_price(symbol, exchange)
                if price_data:
                    return {
                        "symbol": price_data.symbol,
                        "price": price_data.price,
                        "timestamp": price_data.timestamp.isoformat(),
                        "exchange": price_data.exchange,
                        "volume": price_data.volume,
                        "bid": price_data.bid,
                        "ask": price_data.ask,
                        "high_24h": price_data.high_24h,
                        "low_24h": price_data.low_24h,
                    }

            return None
        except Exception as e:
            raise PriceCacheError(f"Failed to get mock exchange data: {e}") from e
