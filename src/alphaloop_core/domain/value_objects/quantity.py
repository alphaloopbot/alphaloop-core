"""Quantity value object for representing trade quantities."""

from decimal import Decimal, InvalidOperation
from typing import Any

from ...shared.exceptions.validation_exceptions import InvalidQuantityError


class Quantity:
    """Immutable value object representing trade quantities."""

    def __init__(self, value: str | float | Decimal, precision: int = 8) -> None:
        """Initialize Quantity with value and precision."""
        self._precision = precision

        try:
            if isinstance(value, str):
                self._value = Decimal(value)
            elif isinstance(value, float):
                self._value = Decimal(str(value))
            elif isinstance(value, Decimal):
                self._value = value
            else:
                raise InvalidQuantityError(f"Invalid quantity type: {type(value)}")
        except (InvalidOperation, ValueError) as e:
            raise InvalidQuantityError(f"Invalid quantity value: {value}") from e

        # Validate quantity is positive
        if self._value <= 0:
            raise InvalidQuantityError("Quantity must be positive")

        # Round to specified precision
        self._value = self._value.quantize(Decimal(f"0.{'0' * precision}"))

    @property
    def value(self) -> Decimal:
        """Get the quantity value as Decimal."""
        return self._value

    @property
    def precision(self) -> int:
        """Get the precision."""
        return self._precision

    def __add__(self, other: "Quantity") -> "Quantity":
        """Add two Quantity objects."""
        if not isinstance(other, Quantity):
            raise TypeError("Can only add Quantity objects")
        max_precision = max(self._precision, other._precision)
        return Quantity(self._value + other._value, max_precision)

    def __sub__(self, other: "Quantity") -> "Quantity":
        """Subtract two Quantity objects."""
        if not isinstance(other, Quantity):
            raise TypeError("Can only subtract Quantity objects")
        result = self._value - other._value
        if result <= 0:
            raise ValueError("Result must be positive")
        max_precision = max(self._precision, other._precision)
        return Quantity(result, max_precision)

    def __mul__(self, multiplier: int | float | Decimal) -> "Quantity":
        """Multiply Quantity by a scalar."""
        if not isinstance(multiplier, int | float | Decimal):
            raise TypeError("Multiplier must be a number")
        return Quantity(self._value * Decimal(str(multiplier)), self._precision)

    def __truediv__(self, divisor: int | float | Decimal) -> "Quantity":
        """Divide Quantity by a scalar."""
        if not isinstance(divisor, int | float | Decimal):
            raise TypeError("Divisor must be a number")
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        return Quantity(self._value / Decimal(str(divisor)), self._precision)

    def __eq__(self, other: Any) -> bool:
        """Check equality."""
        if not isinstance(other, Quantity):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash based on value."""
        return hash(self._value)

    def __lt__(self, other: "Quantity") -> bool:
        """Less than comparison."""
        if not isinstance(other, Quantity):
            raise TypeError("Can only compare with Quantity objects")
        return self._value < other._value

    def __le__(self, other: "Quantity") -> bool:
        """Less than or equal comparison."""
        return self < other or self == other

    def __gt__(self, other: "Quantity") -> bool:
        """Greater than comparison."""
        if not isinstance(other, Quantity):
            raise TypeError("Can only compare with Quantity objects")
        return self._value > other._value

    def __ge__(self, other: "Quantity") -> bool:
        """Greater than or equal comparison."""
        return self > other or self == other

    def __repr__(self) -> str:
        """String representation."""
        return f"Quantity({self._value}, precision={self._precision})"

    def __str__(self) -> str:
        """String representation."""
        return str(self._value)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "value": str(self._value),
            "precision": self._precision,
        }

    @classmethod
    def zero(cls, precision: int = 8) -> "Quantity":
        """Create zero quantity."""
        return cls(Decimal("0"), precision)

    def is_zero(self) -> bool:
        """Check if quantity is zero."""
        return self._value == 0

    def is_positive(self) -> bool:
        """Check if quantity is positive."""
        return self._value > 0

    def round_to_precision(self, precision: int) -> "Quantity":
        """Round quantity to specified precision."""
        return Quantity(self._value, precision)
