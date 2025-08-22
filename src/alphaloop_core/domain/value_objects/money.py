"""Money value object for representing monetary amounts."""

from decimal import Decimal, InvalidOperation
from typing import Any

from ...shared.exceptions.validation_exceptions import InvalidMoneyValueError
from ...shared.types.enums import Currency


class Money:
    """Immutable value object representing monetary amounts."""

    def __init__(self, amount: str | float | Decimal, currency: Currency) -> None:
        """Initialize Money with amount and currency."""
        self._currency = currency

        try:
            if isinstance(amount, str):
                self._amount = Decimal(amount)
            elif isinstance(amount, float):
                self._amount = Decimal(str(amount))
            elif isinstance(amount, Decimal):
                self._amount = amount
            else:
                raise InvalidMoneyValueError(f"Invalid amount type: {type(amount)}")
        except (InvalidOperation, ValueError) as e:
            raise InvalidMoneyValueError(f"Invalid amount value: {amount}") from e

        # Validate amount is not negative
        if self._amount < 0:
            raise InvalidMoneyValueError("Amount cannot be negative")

    @property
    def amount(self) -> Decimal:
        """Get the amount as Decimal."""
        return self._amount

    @property
    def currency(self) -> Currency:
        """Get the currency."""
        return self._currency

    def __add__(self, other: "Money") -> "Money":
        """Add two Money objects."""
        if not isinstance(other, Money):
            raise TypeError("Can only add Money objects")
        if self._currency != other._currency:
            raise ValueError("Cannot add Money objects with different currencies")
        return Money(self._amount + other._amount, self._currency)

    def __sub__(self, other: "Money") -> "Money":
        """Subtract two Money objects."""
        if not isinstance(other, Money):
            raise TypeError("Can only subtract Money objects")
        if self._currency != other._currency:
            raise ValueError("Cannot subtract Money objects with different currencies")
        result = self._amount - other._amount
        if result < 0:
            raise ValueError("Result cannot be negative")
        return Money(result, self._currency)

    def __mul__(self, multiplier: int | float | Decimal) -> "Money":
        """Multiply Money by a scalar."""
        if not isinstance(multiplier, int | float | Decimal):
            raise TypeError("Multiplier must be a number")

        # Convert to Decimal for precise arithmetic
        multiplier_decimal = Decimal(str(multiplier))
        new_amount = self._amount * multiplier_decimal
        return Money(new_amount, self._currency)

    def __truediv__(self, divisor: int | float | Decimal) -> "Money":
        """Divide money by a number."""
        if not isinstance(divisor, int | float | Decimal):
            raise TypeError("Divisor must be a number")
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        return Money(self._amount / Decimal(str(divisor)), self._currency)

    def __eq__(self, other: Any) -> bool:
        """Check equality."""
        if not isinstance(other, Money):
            return False
        return self._amount == other._amount and self._currency == other._currency

    def __hash__(self) -> int:
        """Hash based on amount and currency."""
        return hash((self._amount, self._currency))

    def __lt__(self, other: "Money") -> bool:
        """Less than comparison."""
        if not isinstance(other, Money):
            raise TypeError("Can only compare with Money objects")
        if self._currency != other._currency:
            raise ValueError("Cannot compare Money objects with different currencies")
        return self._amount < other._amount

    def __le__(self, other: "Money") -> bool:
        """Less than or equal comparison."""
        return self < other or self == other

    def __gt__(self, other: "Money") -> bool:
        """Greater than comparison."""
        if not isinstance(other, Money):
            raise TypeError("Can only compare with Money objects")
        if self._currency != other._currency:
            raise ValueError("Cannot compare Money objects with different currencies")
        return self._amount > other._amount

    def __ge__(self, other: "Money") -> bool:
        """Greater than or equal comparison."""
        return self > other or self == other

    def __repr__(self) -> str:
        """String representation."""
        return f"Money({self._amount}, {self._currency.value})"

    def __str__(self) -> str:
        """String representation."""
        return f"{self._amount} {self._currency.value}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "amount": str(self._amount),
            "currency": self._currency.value,
        }

    @classmethod
    def zero(cls, currency: Currency) -> "Money":
        """Create zero amount Money."""
        return cls(Decimal("0"), currency)

    def is_zero(self) -> bool:
        """Check if amount is zero."""
        return self._amount == 0

    def is_positive(self) -> bool:
        """Check if amount is positive."""
        return self._amount > 0
