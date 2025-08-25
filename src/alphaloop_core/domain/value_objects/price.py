"""Price value object for representing prices."""

from decimal import Decimal, InvalidOperation
from typing import Any

from ...shared.exceptions.validation_exceptions import InvalidPriceError
from ...shared.types.enums import Currency


class Price:
    """Immutable value object representing prices."""

    def __init__(self, value: str | float | int | Decimal, currency: Currency) -> None:
        """Initialize Price with value and currency."""
        self._currency = currency

        try:
            if isinstance(value, str):
                self._value = Decimal(value)
            elif isinstance(value, float):
                self._value = Decimal(str(value))
            elif isinstance(value, Decimal):
                self._value = value
            else:
                raise InvalidPriceError(f"Invalid price type: {type(value)}")
        except (InvalidOperation, ValueError) as e:
            raise InvalidPriceError(f"Invalid price value: {value}") from e

        # Validate price is positive
        if self._value <= 0:
            raise InvalidPriceError("Price must be positive")

    @property
    def value(self) -> Decimal:
        """Get the price value as Decimal."""
        return self._value

    @property
    def currency(self) -> Currency:
        """Get the currency."""
        return self._currency

    def __add__(self, other: "Price") -> "Price":
        """Add two Price objects."""
        if not isinstance(other, Price):
            raise TypeError("Can only add Price objects")
        if self._currency != other._currency:
            raise ValueError("Cannot add Price objects with different currencies")
        return Price(self._value + other._value, self._currency)

    def __sub__(self, other: "Price") -> "Price":
        """Subtract two Price objects."""
        if not isinstance(other, Price):
            raise TypeError("Can only subtract Price objects")
        if self._currency != other._currency:
            raise ValueError("Cannot subtract Price objects with different currencies")
        result = self._value - other._value
        if result <= 0:
            raise ValueError("Result must be positive")
        return Price(result, self._currency)

    def __mul__(self, multiplier: int | float | Decimal) -> "Price":
        """Multiply Price by a scalar."""
        if not isinstance(multiplier, int | float | Decimal):
            raise TypeError("Multiplier must be a number")

        # Convert to Decimal for precise arithmetic
        multiplier_decimal = Decimal(str(multiplier))
        new_value = self._value * multiplier_decimal
        return Price(new_value, self._currency)

    def __truediv__(self, divisor: int | float | Decimal) -> "Price":
        """Divide price by a number."""
        if not isinstance(divisor, int | float | Decimal):
            raise TypeError("Divisor must be a number")
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        return Price(self._value / Decimal(str(divisor)), self._currency)

    def __eq__(self, other: Any) -> bool:
        """Check equality."""
        if not isinstance(other, Price):
            return False
        return self._value == other._value and self._currency == other._currency

    def __hash__(self) -> int:
        """Hash based on value and currency."""
        return hash((self._value, self._currency))

    def __lt__(self, other: "Price") -> bool:
        """Less than comparison."""
        if not isinstance(other, Price):
            raise TypeError("Can only compare with Price objects")
        if self._currency != other._currency:
            raise ValueError("Cannot compare Price objects with different currencies")
        return self._value < other._value

    def __le__(self, other: "Price") -> bool:
        """Less than or equal comparison."""
        return self < other or self == other

    def __gt__(self, other: "Price") -> bool:
        """Greater than comparison."""
        if not isinstance(other, Price):
            raise TypeError("Can only compare with Price objects")
        if self._currency != other._currency:
            raise ValueError("Cannot compare Price objects with different currencies")
        return self._value > other._value

    def __ge__(self, other: "Price") -> bool:
        """Greater than or equal comparison."""
        return self > other or self == other

    def __repr__(self) -> str:
        """String representation."""
        return f"Price({self._value}, {self._currency.value})"

    def __str__(self) -> str:
        """String representation."""
        return f"{self._value} {self._currency.value}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "value": str(self._value),
            "currency": self._currency.value,
        }

    def percentage_change(self, other: "Price") -> Decimal:
        """Calculate percentage change from another price."""
        if not isinstance(other, Price):
            raise TypeError("Can only calculate percentage change with Price objects")
        if self._currency != other._currency:
            raise ValueError("Cannot calculate percentage change with different currencies")
        if other._value == 0:
            raise ValueError("Cannot calculate percentage change from zero")
        return ((self._value - other._value) / other._value) * 100

    def is_higher_than(self, other: "Price") -> bool:
        """Check if this price is higher than another."""
        return self > other

    def is_lower_than(self, other: "Price") -> bool:
        """Check if this price is lower than another."""
        return self < other
