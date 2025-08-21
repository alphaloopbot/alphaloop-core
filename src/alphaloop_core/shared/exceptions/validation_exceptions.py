"""Validation-specific exceptions."""

from ..exceptions.base import BaseException


class ValidationError(BaseException):
    """Base class for validation errors."""

    def __init__(self, message: str, field: str | None = None) -> None:
        """Initialize validation error."""
        super().__init__(message)
        self.field = field


class InvalidMoneyValueError(ValidationError):
    """Raised when money value is invalid."""

    def __init__(self, message: str) -> None:
        """Initialize invalid money value error."""
        super().__init__(message, field="amount")


class InvalidPriceError(ValidationError):
    """Raised when price value is invalid."""

    def __init__(self, message: str) -> None:
        """Initialize invalid price error."""
        super().__init__(message, field="price")


class InvalidQuantityError(ValidationError):
    """Raised when quantity value is invalid."""

    def __init__(self, message: str) -> None:
        """Initialize invalid quantity error."""
        super().__init__(message, field="quantity")


class InvalidTimestampError(ValidationError):
    """Raised when timestamp value is invalid."""

    def __init__(self, message: str) -> None:
        """Initialize invalid timestamp error."""
        super().__init__(message, field="timestamp")


class InvalidExchangeIdError(ValidationError):
    """Raised when exchange ID is invalid."""

    def __init__(self, message: str) -> None:
        """Initialize invalid exchange ID error."""
        super().__init__(message, field="exchange_id")


class InvalidPercentageError(ValidationError):
    """Raised when percentage value is invalid."""

    def __init__(self, message: str) -> None:
        """Initialize invalid percentage error."""
        super().__init__(message, field="percentage")


class InvalidSymbolError(ValidationError):
    """Raised when trading symbol is invalid."""

    def __init__(self, message: str) -> None:
        """Initialize invalid symbol error."""
        super().__init__(message, field="symbol")


class InvalidOrderTypeError(ValidationError):
    """Raised when order type is invalid."""

    def __init__(self, message: str) -> None:
        """Initialize invalid order type error."""
        super().__init__(message, field="order_type")


class InvalidOrderSideError(ValidationError):
    """Raised when order side is invalid."""

    def __init__(self, message: str) -> None:
        """Initialize invalid order side error."""
        super().__init__(message, field="order_side")


class InvalidSignalTypeError(ValidationError):
    """Raised when signal type is invalid."""

    def __init__(self, message: str) -> None:
        """Initialize invalid signal type error."""
        super().__init__(message, field="signal_type")


class InvalidTimeframeError(ValidationError):
    """Raised when timeframe is invalid."""

    def __init__(self, message: str) -> None:
        """Initialize invalid timeframe error."""
        super().__init__(message, field="timeframe")


class InvalidCurrencyError(ValidationError):
    """Raised when currency is invalid."""

    def __init__(self, message: str) -> None:
        """Initialize invalid currency error."""
        super().__init__(message, field="currency")
