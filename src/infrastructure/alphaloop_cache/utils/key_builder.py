"""Key builder utilities for AlphaLoop Cache."""

from datetime import datetime


class KeyBuilder:
    """Utility class for building cache keys."""

    def __init__(self, prefix: str = "alphaloop") -> None:
        """Initialize key builder with prefix."""
        self.prefix = prefix

    def _join(self, *segments: str) -> str:
        """Join segments and sanitize final key."""
        raw = ":".join(segments)
        return self.sanitize_key(raw)

    def build_price_key(self, symbol: str, exchange: str) -> str:
        """Build key for price data."""
        return self._join(self.prefix, "price", exchange, symbol)

    def build_price_history_pattern(self, symbol: str, exchange: str) -> str:
        """Build pattern for price history keys."""
        return self._join(self.prefix, "price", exchange, f"{symbol}:*")

    def build_exchange_pattern(self, exchange: str) -> str:
        """Build pattern for exchange keys."""
        return self._join(self.prefix, "price", exchange, "*")

    def build_index_key(self, symbol: str, exchange: str) -> str:
        """Build key for price index."""
        return self._join(self.prefix, "index", exchange, symbol)

    def build_message_key(self, channel: str, timestamp: datetime) -> str:
        """Build key for pub/sub message."""
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S_%f")
        return self._join(self.prefix, "message", channel, timestamp_str)

    def build_channel_pattern(self, channel: str) -> str:
        """Build pattern for channel messages."""
        return self._join(self.prefix, "message", channel, "*")

    def build_user_key(self, user_id: str, data_type: str) -> str:
        """Build key for user data."""
        return self._join(self.prefix, "user", user_id, data_type)

    def build_session_key(self, session_id: str) -> str:
        """Build key for session data."""
        return self._join(self.prefix, "session", session_id)

    def build_lock_key(self, resource: str, identifier: str) -> str:
        """Build key for distributed lock."""
        return self._join(self.prefix, "lock", resource, identifier)

    def build_counter_key(self, name: str, period: str | None = None) -> str:
        """Build key for counter."""
        if period:
            return self._join(self.prefix, "counter", name, period)
        return self._join(self.prefix, "counter", name)

    def build_hash_key(self, name: str, field: str) -> str:
        """Build key for hash field."""
        return self._join(self.prefix, "hash", name, field)

    def build_set_key(self, name: str) -> str:
        """Build key for set."""
        return self._join(self.prefix, "set", name)

    def build_list_key(self, name: str) -> str:
        """Build key for list."""
        return self._join(self.prefix, "list", name)

    def build_sorted_set_key(self, name: str) -> str:
        """Build key for sorted set."""
        return self._join(self.prefix, "zset", name)

    def build_geo_key(self, name: str) -> str:
        """Build key for geospatial data."""
        return self._join(self.prefix, "geo", name)

    def build_stream_key(self, name: str) -> str:
        """Build key for stream."""
        return self._join(self.prefix, "stream", name)

    def build_bitmap_key(self, name: str) -> str:
        """Build key for bitmap."""
        return self._join(self.prefix, "bitmap", name)

    def build_hyperloglog_key(self, name: str) -> str:
        """Build key for hyperloglog."""
        return self._join(self.prefix, "hll", name)

    def build_config_key(self, section: str, key: str) -> str:
        """Build key for configuration."""
        return self._join(self.prefix, "config", section, key)

    def build_metadata_key(self, data_type: str, identifier: str) -> str:
        """Build key for metadata."""
        return self._join(self.prefix, "metadata", data_type, identifier)

    def build_stats_key(self, metric: str, period: str) -> str:
        """Build key for statistics."""
        return self._join(self.prefix, "stats", metric, period)

    def build_cache_key(self, namespace: str, key: str) -> str:
        """Build generic cache key."""
        return self._join(self.prefix, "cache", namespace, key)

    def build_pattern(self, namespace: str, pattern: str = "*") -> str:
        """Build pattern for key scanning."""
        return self._join(self.prefix, namespace, pattern)

    def parse_key(self, key: str) -> dict[str, str]:
        """Parse key into components."""
        parts = key.split(":")
        if len(parts) < 2:
            return {"prefix": parts[0] if parts else "", "type": "unknown"}

        result = {"prefix": parts[0]}

        if len(parts) >= 2:
            result["type"] = parts[1]

        if len(parts) >= 3:
            result["namespace"] = parts[2]

        if len(parts) >= 4:
            result["identifier"] = parts[3]

        return result

    def is_valid_key(self, key: str) -> bool:
        """Check if key is valid."""
        if not key or len(key) > 512:  # Redis key length limit
            return False

        # Check for invalid characters
        invalid_chars = ["\x00", "\r", "\n"]
        return not any(char in key for char in invalid_chars)

    def sanitize_key(self, key: str) -> str:
        """Sanitize key for safe storage."""
        # Replace invalid characters
        sanitized = key.replace("\x00", "").replace("\r", "").replace("\n", "")

        # Limit length
        if len(sanitized) > 512:
            sanitized = sanitized[:512]

        return sanitized
