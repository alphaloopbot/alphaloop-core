"""Use case for orchestrating the scraping of market data from exchanges."""

from ....domain.entities.ticker import Ticker
from ....domain.repositories.ticker_repository import TickerRepository
from ....domain.services.exchange_service import ExchangeService
from ....domain.services.market_data_service import MarketDataService
from ....domain.value_objects.exchange_id import ExchangeId
from ....shared.exceptions.application_exceptions import MarketDataScrapingError
from ....shared.types.enums import MarketDataType, Timeframe


class ScrapeMarketDataUseCase:
    """Orchestrates the scraping of market data from exchanges."""

    def __init__(
        self,
        ticker_repository: TickerRepository,
        market_data_service: MarketDataService,
        exchange_service: ExchangeService,
    ) -> None:
        """Initialize the use case with dependencies."""
        self._ticker_repository = ticker_repository
        self._market_data_service = market_data_service
        self._exchange_service = exchange_service

    async def execute(
        self,
        exchange_id: ExchangeId,
        symbols: list[str] | None = None,
        data_types: list[MarketDataType] | None = None,
        timeframe: Timeframe | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        Execute the market data scraping use case.

        Args:
            exchange_id: The exchange to scrape data from
            symbols: List of symbols to scrape (if None, scrape all available)
            data_types: Types of market data to scrape
            timeframe: Timeframe for the data
            limit: Maximum number of data points to scrape

        Returns:
            Dictionary containing scraping results and statistics

        Raises:
            MarketDataScrapingError: If scraping fails
        """
        try:
            # Validate exchange is available
            if not await self._exchange_service.is_exchange_available(exchange_id):
                raise MarketDataScrapingError(f"Exchange {exchange_id} is not available")

            # Get tickers to scrape
            if symbols:
                tickers = []
                for symbol in symbols:
                    ticker = await self._ticker_repository.find_by_exchange_and_symbol(
                        exchange_id, symbol
                    )
                    if ticker:
                        tickers.append(ticker)
                    else:
                        # Log warning for missing ticker
                        print(f"Warning: Ticker {symbol} not found for exchange {exchange_id}")
            else:
                tickers = await self._ticker_repository.find_by_exchange(exchange_id)

            if not tickers:
                raise MarketDataScrapingError(f"No tickers found for exchange {exchange_id}")

            # Set default data types if not specified
            if data_types is None:
                data_types = [MarketDataType.TICKER, MarketDataType.TRADE]

            # Set default timeframe if not specified
            if timeframe is None:
                timeframe = Timeframe.MINUTE_1

            # Initialize results tracking
            results = {
                "exchange_id": str(exchange_id),
                "total_tickers": len(tickers),
                "data_types": [dt.value for dt in data_types],
                "timeframe": timeframe.value,
                "scraped_data": [],
                "errors": [],
                "statistics": {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "total_data_points": 0,
                },
            }

            # Scrape data for each ticker
            for ticker in tickers:
                try:
                    ticker_results = await self._scrape_ticker_data(
                        ticker, data_types, timeframe, limit
                    )
                    results["scraped_data"].append(ticker_results)
                    results["statistics"]["successful_requests"] += 1
                    results["statistics"]["total_data_points"] += ticker_results.get(
                        "data_points", 0
                    )
                except Exception as e:
                    error_info = {
                        "ticker": ticker.symbol,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    }
                    results["errors"].append(error_info)
                    results["statistics"]["failed_requests"] += 1

                results["statistics"]["total_requests"] += 1

            # Add summary statistics
            results["statistics"]["success_rate"] = (
                results["statistics"]["successful_requests"]
                / results["statistics"]["total_requests"]
                if results["statistics"]["total_requests"] > 0
                else 0
            )

            return results

        except Exception as e:
            raise MarketDataScrapingError(f"Market data scraping failed: {str(e)}") from e

    async def _scrape_ticker_data(
        self,
        ticker: Ticker,
        data_types: list[MarketDataType],
        timeframe: Timeframe,
        limit: int | None,
    ) -> dict:
        """Scrape data for a specific ticker."""
        ticker_results = {
            "ticker_id": str(ticker.id),
            "symbol": ticker.symbol,
            "base_currency": ticker.base_currency.value,
            "quote_currency": ticker.quote_currency.value,
            "data": {},
            "data_points": 0,
            "timestamp": None,
        }

        for data_type in data_types:
            try:
                data = await self._market_data_service.scrape_data(
                    ticker, data_type, timeframe, limit
                )
                ticker_results["data"][data_type.value] = data
                ticker_results["data_points"] += len(data) if data else 0
                last_ts = data[-1].get("timestamp") if data and isinstance(data[-1], dict) else None
                if last_ts is not None:
                    ticker_results["timestamp"] = last_ts
            except Exception as e:
                ticker_results["data"][data_type.value] = {"error": str(e)}

        return ticker_results

    async def execute_for_all_exchanges(
        self,
        symbols: list[str] | None = None,
        data_types: list[MarketDataType] | None = None,
        timeframe: Timeframe | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        Execute scraping for all available exchanges.

        Args:
            symbols: List of symbols to scrape (if None, scrape all available)
            data_types: Types of market data to scrape
            timeframe: Timeframe for the data
            limit: Maximum number of data points to scrape

        Returns:
            Dictionary containing results for all exchanges
        """
        available_exchanges = await self._exchange_service.get_available_exchanges()

        all_results = {
            "total_exchanges": len(available_exchanges),
            "exchange_results": [],
            "overall_statistics": {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_data_points": 0,
            },
        }

        for exchange_id in available_exchanges:
            try:
                exchange_result = await self.execute(
                    exchange_id, symbols, data_types, timeframe, limit
                )
                all_results["exchange_results"].append(exchange_result)

                # Aggregate statistics
                stats = exchange_result["statistics"]
                all_results["overall_statistics"]["total_requests"] += stats["total_requests"]
                all_results["overall_statistics"]["successful_requests"] += stats[
                    "successful_requests"
                ]
                all_results["overall_statistics"]["failed_requests"] += stats["failed_requests"]
                all_results["overall_statistics"]["total_data_points"] += stats["total_data_points"]

            except Exception as e:
                error_result = {
                    "exchange_id": str(exchange_id),
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
                all_results["exchange_results"].append(error_result)

        # Calculate overall success rate
        total_requests = all_results["overall_statistics"]["total_requests"]
        if total_requests > 0:
            all_results["overall_statistics"]["success_rate"] = (
                all_results["overall_statistics"]["successful_requests"] / total_requests
            )
        else:
            all_results["overall_statistics"]["success_rate"] = 0

        return all_results
