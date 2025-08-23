"""Cache entry model for AlphaLoop Cache."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class CacheEntry(BaseModel):
    """Cache entry with metadata."""

    key: str
    data: dict[str, Any]
    timestamp: datetime
    ttl: int
    version: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "ttl": self.ttl,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CacheEntry":
        """Create from dictionary."""
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl <= 0:
            return False  # No expiration

        expiry_time = self.timestamp.timestamp() + self.ttl
        return datetime.utcnow().timestamp() > expiry_time

    def get_remaining_ttl(self) -> int:
        """Get remaining TTL in seconds."""
        if self.ttl <= 0:
            return -1  # No expiration

        expiry_time = self.timestamp.timestamp() + self.ttl
        remaining = int(expiry_time - datetime.utcnow().timestamp())
        return max(0, remaining)

    def __repr__(self) -> str:
        """String representation."""
        return f"<CacheEntry(key='{self.key}', ttl={self.ttl}s, expired={self.is_expired()})>"
