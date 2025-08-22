"""Market data service interface."""

from abc import ABC, abstractmethod
from typing import Any

from ...shared.types.enums import MarketDataType, Timeframe
from ..entities.ticker import Ticker


class MarketDataService(ABC):
    """Abstract market data service interface."""

    @abstractmethod
    async def scrape_data(
        self,
        ticker: Ticker,
        data_type: MarketDataType,
        timeframe: Timeframe,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Scrape market data for a specific ticker."""
        pass

    @abstractmethod
    async def process_data(
        self, raw_data: list[dict[str, Any]], data_type: MarketDataType
    ) -> list[dict[str, Any]]:
        """Process raw market data."""
        pass

    @abstractmethod
    async def store_data(self, processed_data: list[dict[str, Any]], ticker: Ticker) -> bool:
        """Store processed market data."""
        pass

    @abstractmethod
    async def retrieve_data(
        self,
        ticker: Ticker,
        data_type: MarketDataType,
        timeframe: Timeframe,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve stored market data."""
        pass
