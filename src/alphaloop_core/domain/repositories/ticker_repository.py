"""Interface for ticker data access operations."""

from abc import abstractmethod
from typing import Any

from ...shared.types.enums import Currency, ExchangeType
from ..entities.ticker import Ticker
from ..value_objects.exchange_id import ExchangeId
from .base import Repository


class TickerRepository(Repository[Ticker]):
    """Interface for ticker data access operations."""

    @abstractmethod
    async def find_by_symbol(self, symbol: str) -> Ticker | None:
        """Find a ticker by its symbol."""
        pass

    @abstractmethod
    async def find_by_exchange(self, exchange_id: ExchangeId) -> list[Ticker]:
        """Find all tickers for a specific exchange."""
        pass

    @abstractmethod
    async def find_by_currencies(
        self, base_currency: Currency, quote_currency: Currency
    ) -> list[Ticker]:
        """Find tickers by base and quote currencies."""
        pass

    @abstractmethod
    async def find_by_exchange_type(self, exchange_type: ExchangeType) -> list[Ticker]:
        """Find tickers by exchange type (spot, futures, options)."""
        pass

    @abstractmethod
    async def find_active_tickers(self) -> list[Ticker]:
        """Find all active tickers."""
        pass

    @abstractmethod
    async def find_by_symbol_pattern(self, pattern: str) -> list[Ticker]:
        """Find tickers by symbol pattern (e.g., 'BTC*' for all BTC pairs)."""
        pass

    @abstractmethod
    async def find_by_base_currency(self, base_currency: Currency) -> list[Ticker]:
        """Find all tickers with a specific base currency."""
        pass

    @abstractmethod
    async def find_by_quote_currency(self, quote_currency: Currency) -> list[Ticker]:
        """Find all tickers with a specific quote currency."""
        pass

    @abstractmethod
    async def find_spot_tickers(self) -> list[Ticker]:
        """Find all spot trading tickers."""
        pass

    @abstractmethod
    async def find_futures_tickers(self) -> list[Ticker]:
        """Find all futures trading tickers."""
        pass

    @abstractmethod
    async def find_options_tickers(self) -> list[Ticker]:
        """Find all options trading tickers."""
        pass

    @abstractmethod
    async def find_by_exchange_and_symbol(
        self, exchange_id: ExchangeId, symbol: str
    ) -> Ticker | None:
        """Find a ticker by exchange and symbol combination."""
        pass

    @abstractmethod
    async def find_by_exchange_and_currencies(
        self,
        exchange_id: ExchangeId,
        base_currency: Currency,
        quote_currency: Currency,
    ) -> Ticker | None:
        """Find a ticker by exchange and currency pair combination."""
        pass

    @abstractmethod
    async def get_popular_tickers(self, limit: int = 10) -> list[Ticker]:
        """Get the most popular tickers (based on trading volume or other metrics)."""
        pass

    @abstractmethod
    async def get_tickers_with_volume_above(
        self, min_volume: float, timeframe: str = "24h"
    ) -> list[Ticker]:
        """Get tickers with trading volume above a threshold."""
        pass

    @abstractmethod
    async def get_tickers_by_market_cap(
        self, min_market_cap: float, limit: int = 100
    ) -> list[Ticker]:
        """Get tickers by market capitalization."""
        pass

    @abstractmethod
    async def search_tickers(
        self,
        query: str,
        exchange_id: ExchangeId | None = None,
        exchange_type: ExchangeType | None = None,
        limit: int = 50,
    ) -> list[Ticker]:
        """Search tickers by query string with optional filters."""
        pass

    @abstractmethod
    async def get_ticker_statistics(self, ticker_id: str) -> dict[str, Any]:
        """Get statistics for a specific ticker."""
        pass

    @abstractmethod
    async def get_exchange_statistics(self, exchange_id: ExchangeId) -> dict[str, Any]:
        """Get statistics for all tickers on a specific exchange."""
        pass

    @abstractmethod
    async def get_currency_statistics(self, currency: Currency) -> dict[str, Any]:
        """Get statistics for all tickers involving a specific currency."""
        pass
