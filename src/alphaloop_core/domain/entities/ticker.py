"""Ticker entity representing a trading pair."""

from typing import Any

from ...shared.exceptions.validation_exceptions import InvalidSymbolError
from ...shared.types.enums import Currency, ExchangeType
from ..value_objects.exchange_id import ExchangeId
from ..value_objects.quantity import Quantity
from .base import Entity


class Ticker(Entity):
    """Represents a trading pair with symbol, base/quote currencies, and exchange info."""

    def __init__(
        self,
        symbol: str,
        base_currency: Currency,
        quote_currency: Currency,
        exchange_id: ExchangeId,
        exchange_type: ExchangeType = ExchangeType.SPOT,
        min_quantity: Quantity | None = None,
        max_quantity: Quantity | None = None,
        tick_size: float | None = None,
        step_size: float | None = None,
        is_active: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialize Ticker entity."""
        super().__init__(**kwargs)

        self._symbol = self._validate_symbol(symbol)
        self._base_currency = base_currency
        self._quote_currency = quote_currency
        self._exchange_id = exchange_id
        self._exchange_type = exchange_type
        self._min_quantity = min_quantity
        self._max_quantity = max_quantity
        self._tick_size = tick_size
        self._step_size = step_size
        self._is_active = is_active

    @property
    def symbol(self) -> str:
        """Get the trading symbol."""
        return self._symbol

    @property
    def base_currency(self) -> Currency:
        """Get the base currency."""
        return self._base_currency

    @property
    def quote_currency(self) -> Currency:
        """Get the quote currency."""
        return self._quote_currency

    @property
    def exchange_id(self) -> ExchangeId:
        """Get the exchange ID."""
        return self._exchange_id

    @property
    def exchange_type(self) -> ExchangeType:
        """Get the exchange type."""
        return self._exchange_type

    @property
    def min_quantity(self) -> Quantity | None:
        """Get the minimum quantity."""
        return self._min_quantity

    @property
    def max_quantity(self) -> Quantity | None:
        """Get the maximum quantity."""
        return self._max_quantity

    @property
    def tick_size(self) -> float | None:
        """Get the tick size."""
        return self._tick_size

    @property
    def step_size(self) -> float | None:
        """Get the step size."""
        return self._step_size

    def is_active(self) -> bool:
        """Check if the ticker is active."""
        return self._is_active and super().is_active()

    def _validate_symbol(self, symbol: str) -> str:
        """Validate the trading symbol."""
        if not symbol or not symbol.strip():
            raise InvalidSymbolError("Symbol cannot be empty")

        symbol = symbol.strip().upper()

        # Basic symbol validation (can be enhanced based on exchange requirements)
        if len(symbol) < 2:
            raise InvalidSymbolError("Symbol must be at least 2 characters long")

        if len(symbol) > 20:
            raise InvalidSymbolError("Symbol cannot exceed 20 characters")

        # Check for valid characters (letters, numbers, and common separators)
        import re

        if not re.match(r"^[A-Z0-9/_-]+$", symbol):
            raise InvalidSymbolError("Symbol contains invalid characters")

        return symbol

    def activate(self) -> None:
        """Activate the ticker."""
        self._is_active = True
        super().activate()

    def deactivate(self) -> None:
        """Deactivate the ticker."""
        self._is_active = False
        super().deactivate()

    def validate(self) -> bool:
        """Validate the ticker state."""
        try:
            # Validate symbol
            self._validate_symbol(self._symbol)

            # Validate currencies are different
            if self._base_currency == self._quote_currency:
                raise InvalidSymbolError("Base and quote currencies must be different")

            # Validate quantity constraints
            if self._min_quantity and self._max_quantity:
                if self._min_quantity >= self._max_quantity:
                    raise ValueError("Minimum quantity must be less than maximum quantity")

            # Validate tick and step sizes
            if self._tick_size is not None and self._tick_size <= 0:
                raise ValueError("Tick size must be positive")

            if self._step_size is not None and self._step_size <= 0:
                raise ValueError("Step size must be positive")

            return True
        except Exception:
            return False

    def to_dict(self) -> dict[str, Any]:
        """Convert ticker to dictionary representation."""
        return {
            "id": str(self.id),
            "symbol": self._symbol,
            "base_currency": self._base_currency.value,
            "quote_currency": self._quote_currency.value,
            "exchange_id": str(self._exchange_id),
            "exchange_type": self._exchange_type.value,
            "min_quantity": str(self._min_quantity) if self._min_quantity else None,
            "max_quantity": str(self._max_quantity) if self._max_quantity else None,
            "tick_size": self._tick_size,
            "step_size": self._step_size,
            "is_active": self.is_active(),
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __repr__(self) -> str:
        """String representation of the ticker."""
        return f"Ticker(symbol='{self._symbol}', exchange='{self._exchange_id}')"

    def __str__(self) -> str:
        """String representation of the ticker."""
        return f"{self._symbol} on {self._exchange_id}"

    def get_pair_name(self) -> str:
        """Get the currency pair name."""
        return f"{self._base_currency.value}/{self._quote_currency.value}"

    def is_spot_trading(self) -> bool:
        """Check if this is a spot trading pair."""
        return self._exchange_type == ExchangeType.SPOT

    def is_futures_trading(self) -> bool:
        """Check if this is a futures trading pair."""
        return self._exchange_type == ExchangeType.FUTURES

    def is_options_trading(self) -> bool:
        """Check if this is an options trading pair."""
        return self._exchange_type == ExchangeType.OPTIONS
