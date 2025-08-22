"""Ticker metadata entity for market instrument definitions."""

from datetime import datetime
from typing import Any
from uuid import UUID

from alphaloop_core.domain.entities.base import Entity
from alphaloop_core.domain.value_objects.exchange_id import ExchangeId


class TickerMetadata(Entity):
    """Ticker metadata entity representing market instrument definitions."""

    def __init__(
        self,
        ticker: str,
        base: str,
        quote: str,
        exchange: str,
        active: bool,
        entity_id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize the ticker metadata entity."""
        super().__init__(entity_id, created_at, updated_at)

        self._ticker = ticker.upper()
        self._base = base.upper()
        self._quote = quote.upper()
        self._exchange = ExchangeId(exchange)
        self._active = active

    @property
    def ticker(self) -> str:
        """Get the ticker symbol."""
        return self._ticker

    @property
    def base(self) -> str:
        """Get the base currency."""
        return self._base

    @property
    def quote(self) -> str:
        """Get the quote currency."""
        return self._quote

    @property
    def exchange(self) -> ExchangeId:
        """Get the exchange identifier."""
        return self._exchange

    @property
    def active(self) -> bool:
        """Check if the ticker is active."""
        return self._active

    def activate(self) -> None:
        """Activate the ticker."""
        self._active = True
        self.update_timestamp()

    def deactivate(self) -> None:
        """Deactivate the ticker."""
        self._active = False
        self.update_timestamp()

    def validate(self) -> bool:
        """Validate the ticker metadata."""
        return (
            bool(self._ticker)
            and bool(self._base)
            and bool(self._quote)
            and bool(self._exchange.value)
            and self._ticker != self._base
            and self._ticker != self._quote
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the entity to a dictionary."""
        base_dict = super().to_dict()
        return {
            **base_dict,
            "ticker": self._ticker,
            "base": self._base,
            "quote": self._quote,
            "exchange": self._exchange.value,
            "active": self._active,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TickerMetadata":
        """Create a TickerMetadata entity from a dictionary."""
        return cls(
            ticker=data["ticker"],
            base=data["base"],
            quote=data["quote"],
            exchange=data["exchange"],
            active=data["active"],
            entity_id=UUID(data["id"]) if data.get("id") else None,
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else None,
            updated_at=datetime.fromisoformat(data["updated_at"])
            if data.get("updated_at")
            else None,
        )
