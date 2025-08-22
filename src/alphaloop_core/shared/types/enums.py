"""Enumeration definitions for shared types."""

from enum import Enum


class EntityStatus(Enum):
    """Entity status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"


class OrderType(Enum):
    """Order type enumeration."""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    """Order side enumeration."""

    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Order status enumeration."""

    PENDING = "pending"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class SignalType(Enum):
    """Signal type enumeration."""

    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class SignalStrength(Enum):
    """Signal strength enumeration."""

    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"


class ExchangeType(Enum):
    """Exchange type enumeration."""

    SPOT = "spot"
    FUTURES = "futures"
    OPTIONS = "options"


class MarketDataType(Enum):
    """Market data type enumeration."""

    TICKER = "ticker"
    TRADE = "trade"
    ORDERBOOK = "orderbook"
    OHLCV = "ohlcv"


class Timeframe(Enum):
    """Timeframe enumeration."""

    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    HOUR_12 = "12h"
    DAY_1 = "1d"
    WEEK_1 = "1w"
    MONTH_1 = "1M"


class Currency(Enum):
    """Currency enumeration."""

    USD = "USD"
    EUR = "EUR"
    BTC = "BTC"
    ETH = "ETH"
    USDT = "USDT"
    USDC = "USDC"


class LogLevel(Enum):
    """Log level enumeration."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Environment(Enum):
    """Environment enumeration."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"
