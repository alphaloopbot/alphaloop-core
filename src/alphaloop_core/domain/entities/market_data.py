"""Market data entity for price and volume information."""

from datetime import datetime
from typing import Any
from uuid import UUID

from alphaloop_core.config import get_default_currency
from alphaloop_core.domain.entities.base import Entity
from alphaloop_core.domain.value_objects.price import Price
from alphaloop_core.domain.value_objects.quantity import Quantity
from alphaloop_core.shared.types.enums import Currency


class MarketData(Entity):
    """Market data entity representing price and volume information."""

    def __init__(
        self,
        metadata_id: int,
        timestamp_id: int,
        price: float,
        quote_volume24h: float,
        currency: Currency | None = None,
        entity_id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize the market data entity."""
        super().__init__(entity_id, created_at, updated_at)

        self._metadata_id = int(metadata_id)
        self._timestamp_id = timestamp_id
        self._price = Price(price, currency or get_default_currency())
        self._quote_volume24h = Quantity(quote_volume24h)

    @property
    def metadata_id(self) -> int:
        """Get the metadata ID reference."""
        return self._metadata_id

    @property
    def timestamp_id(self) -> int:
        """Get the timestamp ID."""
        return self._timestamp_id

    @property
    def price(self) -> Price:
        """Get the price value object."""
        return self._price

    @property
    def quote_volume24h(self) -> Quantity:
        """Get the 24-hour quote volume value object."""
        return self._quote_volume24h

    def validate(self) -> bool:
        """Validate the market data."""
        return (
            bool(self._metadata_id)
            and self._timestamp_id > 0
            and self._price.value > 0
            and self._quote_volume24h.value >= 0
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the entity to a dictionary."""
        base_dict = super().to_dict()
        return {
            **base_dict,
            "metadata_id": self._metadata_id,
            "timestamp_id": self._timestamp_id,
            "price": str(self._price.value),
            "quote_volume24h": str(self._quote_volume24h.value),
            "currency": self._price.currency.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MarketData":
        """Create a MarketData entity from a dictionary."""
        currency = None
        if "currency" in data:
            currency = Currency(data["currency"])

        return cls(
            metadata_id=data["metadata_id"],
            timestamp_id=data["timestamp_id"],
            price=data["price"],
            quote_volume24h=data["quote_volume24h"],
            currency=currency,
            entity_id=UUID(data["id"]) if data.get("id") else None,
            created_at=(
                datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
            ),
            updated_at=(
                datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
            ),
        )
