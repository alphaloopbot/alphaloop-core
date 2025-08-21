"""Exchange ID value object for representing exchange identifiers."""

import re
from typing import Any

from ...shared.exceptions.validation_exceptions import InvalidExchangeIdError


class ExchangeId:
    """Immutable value object representing exchange identifiers."""

    def __init__(self, value: str) -> None:
        """Initialize ExchangeId with value."""
        self._value = self._validate_exchange_id(value)

    @property
    def value(self) -> str:
        """Get the exchange ID value."""
        return self._value

    def _validate_exchange_id(self, exchange_id: str) -> str:
        """Validate the exchange ID."""
        if not exchange_id or not exchange_id.strip():
            raise InvalidExchangeIdError("Exchange ID cannot be empty")

        exchange_id = exchange_id.strip().lower()

        # Basic validation for exchange ID format
        if len(exchange_id) < 2:
            raise InvalidExchangeIdError("Exchange ID must be at least 2 characters long")

        if len(exchange_id) > 50:
            raise InvalidExchangeIdError("Exchange ID cannot exceed 50 characters")

        # Check for valid characters (letters, numbers, hyphens, underscores)
        if not re.match(r"^[a-z0-9_-]+$", exchange_id):
            raise InvalidExchangeIdError("Exchange ID contains invalid characters")

        return exchange_id

    def __eq__(self, other: Any) -> bool:
        """Check equality."""
        if not isinstance(other, ExchangeId):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash based on value."""
        return hash(self._value)

    def __lt__(self, other: "ExchangeId") -> bool:
        """Less than comparison."""
        if not isinstance(other, ExchangeId):
            raise TypeError("Can only compare with ExchangeId objects")
        return self._value < other._value

    def __le__(self, other: "ExchangeId") -> bool:
        """Less than or equal comparison."""
        return self < other or self == other

    def __gt__(self, other: "ExchangeId") -> bool:
        """Greater than comparison."""
        if not isinstance(other, ExchangeId):
            raise TypeError("Can only compare with ExchangeId objects")
        return self._value > other._value

    def __ge__(self, other: "ExchangeId") -> bool:
        """Greater than or equal comparison."""
        return self > other or self == other

    def __repr__(self) -> str:
        """String representation."""
        return f"ExchangeId('{self._value}')"

    def __str__(self) -> str:
        """String representation."""
        return self._value

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {"value": self._value}
