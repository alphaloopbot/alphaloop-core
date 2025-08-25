"""Price caching service for AlphaLoop Core."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from infrastructure.alphaloop_cache.core.connection import CacheManager
from infrastructure.alphaloop_cache.core.generic_cache import GenericCache


class PriceData(BaseModel):
    """Price data model for market data."""

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


class PriceCacheService:
    """Price caching service using generic cache infrastructure."""

    def __init__(
        self,
        cache_manager: CacheManager,
        default_ttl: int = 300,  # 5 minutes
        max_cache_size: int = 10000,
    ) -> None:
        """Initialize price cache service."""
        self.generic_cache = GenericCache(
            cache_manager=cache_manager,
            default_ttl=default_ttl,
            max_cache_size=max_cache_size,
            prefix="price",
        )

    def _build_price_key(self, symbol: str, exchange: str) -> str:
        """Build cache key for price data."""
        return f"price:{exchange}:{symbol}"

    def _build_price_history_pattern(self, symbol: str, exchange: str) -> str:
        """Build pattern for price history keys."""
        return f"price:{exchange}:{symbol}:*"

    def _build_exchange_pattern(self, exchange: str) -> str:
        """Build pattern for exchange keys."""
        return f"price:{exchange}:*"

    async def cache_price(self, price_data: PriceData, ttl: int | None = None) -> bool:
        """Cache price data."""
        try:
            key = self._build_price_key(price_data.symbol, price_data.exchange)
            value = price_data.to_dict()

            success = await self.generic_cache.set_data(key, value, ttl)

            if success:
                await self._update_price_index(price_data.symbol, price_data.exchange)

            return success
        except Exception as e:
            raise Exception(f"Failed to cache price for {price_data.symbol}: {e}") from e

    async def get_price(self, symbol: str, exchange: str) -> PriceData | None:
        """Get cached price data."""
        try:
            key = self._build_price_key(symbol, exchange)
            cached_data = await self.generic_cache.get_data(key)

            if cached_data is None:
                return None

            # Parse price data
            return PriceData.from_dict(cached_data)
        except Exception as e:
            raise Exception(f"Failed to get price for {symbol}: {e}") from e

    async def get_latest_prices(self, symbols: list[str], exchange: str) -> dict[str, PriceData]:
        """Get latest prices for multiple symbols."""
        try:
            result = {}
            for symbol in symbols:
                price_data = await self.get_price(symbol, exchange)
                if price_data:
                    result[symbol] = price_data
            return result
        except Exception as e:
            raise Exception(f"Failed to get latest prices: {e}") from e

    async def get_price_history(
        self, symbol: str, exchange: str, hours: int = 24
    ) -> list[PriceData]:
        """Get price history for a symbol."""
        try:
            pattern = self._build_price_history_pattern(symbol, exchange)
            history_data = await self.generic_cache.get_history(pattern, hours)

            history = []
            for entry in history_data:
                price_data = PriceData.from_dict(entry["data"])
                history.append(price_data)

            return history
        except Exception as e:
            raise Exception(f"Failed to get price history for {symbol}: {e}") from e

    async def invalidate_price(self, symbol: str, exchange: str) -> bool:
        """Invalidate cached price."""
        try:
            key = self._build_price_key(symbol, exchange)
            return await self.generic_cache.delete_data(key)
        except Exception as e:
            raise Exception(f"Failed to invalidate price for {symbol}: {e}") from e

    async def invalidate_exchange_prices(self, exchange: str) -> int:
        """Invalidate all prices for an exchange."""
        try:
            pattern = self._build_exchange_pattern(exchange)
            return await self.generic_cache.delete_by_pattern(pattern)
        except Exception as e:
            raise Exception(f"Failed to invalidate exchange prices: {e}") from e

    async def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        try:
            stats = await self.generic_cache.get_cache_stats()
            return {
                "total_keys": stats["total_keys"],
                "price_keys": stats["pattern_keys"],
                "memory_usage": stats["memory_usage"],
                "default_ttl": stats["default_ttl"],
                "max_cache_size": stats["max_cache_size"],
            }
        except Exception as e:
            raise Exception(f"Failed to get cache stats: {e}") from e

    async def cleanup_expired(self) -> int:
        """Clean up expired cache entries."""
        try:
            return await self.generic_cache.cleanup_expired()
        except Exception as e:
            raise Exception(f"Failed to cleanup expired entries: {e}") from e

    async def _update_price_index(self, symbol: str, exchange: str) -> None:
        """Update price index for quick lookups."""
        try:
            index_key = f"price:index:{exchange}:{symbol}"
            timestamp = datetime.utcnow().isoformat()
            await self.generic_cache.set_data(
                index_key, timestamp, ttl=self.generic_cache.default_ttl
            )
        except Exception as e:
            # Log but don't fail the main operation
            print(f"Warning: Failed to update price index: {e}")

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
            raise Exception(f"Failed to get mock exchange data: {e}") from e
