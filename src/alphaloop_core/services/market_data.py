"""
Market Data Service

This service collects market data from exchanges and stores it in the database.
Uses alphaloop infrastructure packages for logging, storage, cache, and heartbeat monitoring.
"""

import asyncio
import os
import random
import time
from typing import Any

from infrastructure.alphaloop_cache import create_cache_manager
from infrastructure.alphaloop_heartbeat import HeartbeatGenerator
from infrastructure.alphaloop_logging import AlphaLoopLogger, LoggingConfig
from infrastructure.alphaloop_storage import TableHandler, create_database_manager

from .cache import PriceCacheService


class MarketDataService:
    """Market data collection service using alphaloop infrastructure."""

    def __init__(self) -> None:
        """Initialize the market data service with infrastructure components."""
        # Initialize infrastructure components
        logging_config = LoggingConfig.from_env(app_name="market-data-service")
        self.logger = AlphaLoopLogger(logging_config)

        # Create database manager from environment variables
        self.db_manager = create_database_manager(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "alphaloop_market"),
            username=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            port=int(os.getenv("DB_PORT", "5432")),
        )

        # Initialize table handlers for both metadata and data
        self.metadata_handler = TableHandler("tickers_metadata", self.db_manager)
        self.data_handler = TableHandler("tickers_prices", self.db_manager)
        self.cache_manager = create_cache_manager()
        self.price_cache = PriceCacheService(self.cache_manager)
        self.heartbeat_generator = HeartbeatGenerator("market-data")

        # Configuration
        self.market_data_interval = int(os.getenv("MARKET_DATA_INTERVAL", 60))
        self.deployment_type = os.getenv("DEPLOYMENT_TYPE", "local")
        self.cloud_sync_enabled = os.getenv("CLOUD_SYNC_ENABLED", "false").lower() == "true"
        self.cloud_sync_interval = int(os.getenv("CLOUD_SYNC_INTERVAL", 300))
        self.cloud_api_url = os.getenv("CLOUD_API_URL", "")

        # Get or create market metadata (will be initialized in first async call)
        self.metadata_ids = None

        self.logger.info_sync(f"Deployment type: {self.deployment_type}")
        self.logger.info_sync(f"Cloud sync enabled: {self.cloud_sync_enabled}")
        self.logger.info_sync(
            f"Market Data Service initialized (interval: {self.market_data_interval}s)"
        )

    async def _get_or_create_metadata(self) -> dict[str, int | None]:
        """Get existing metadata or create new ones for trading pairs."""
        try:
            # Define the trading pairs we want to track
            trading_pairs = [
                {
                    "symbol": "BTC/USDT",
                    "base": "BTC",
                    "quote": "USDT",
                    "exchange": "binance",
                },
                {
                    "symbol": "ETH/USDT",
                    "base": "ETH",
                    "quote": "USDT",
                    "exchange": "binance",
                },
                {
                    "symbol": "ADA/USDT",
                    "base": "ADA",
                    "quote": "USDT",
                    "exchange": "binance",
                },
                {
                    "symbol": "DOT/USDT",
                    "base": "DOT",
                    "quote": "USDT",
                    "exchange": "binance",
                },
            ]

            metadata_ids = {}

            for pair in trading_pairs:
                # For now, we'll create new metadata each time (in production, you'd query existing)
                metadata = {
                    "ticker": pair["symbol"],
                    "base": pair["base"],
                    "quote": pair["quote"],
                    "exchange": pair["exchange"],
                    "active": True,
                }

                # Insert metadata and store the ID
                metadata_id = await self.metadata_handler.insert_data(metadata)
                if metadata_id is not None:
                    if isinstance(metadata_id, list):
                        if metadata_id:
                            metadata_ids[pair["symbol"]] = metadata_id[0]
                        else:
                            raise ValueError(
                                f"Failed to insert metadata for {pair['symbol']}: empty result"
                            )
                    else:
                        metadata_ids[pair["symbol"]] = metadata_id
                else:
                    raise ValueError(
                        f"Failed to insert metadata for {pair['symbol']}: no ID returned"
                    )

            return metadata_ids

        except Exception as e:
            self.logger.error_sync(f"Error creating metadata: {e}")
            raise RuntimeError(f"Failed to create metadata: {e}") from e

    async def get_mock_market_data(self) -> list[dict[str, Any]]:
        """Generate mock market data for testing."""
        # Initialize metadata_ids if not set
        if self.metadata_ids is None:
            self.metadata_ids = await self._get_or_create_metadata()

        mock_data = []
        symbols = list(self.metadata_ids.keys())

        for symbol in symbols:
            # Generate realistic price movements
            base_price = {
                "BTC/USDT": 45000,
                "ETH/USDT": 3000,
                "ADA/USDT": 0.5,
                "DOT/USDT": 7,
            }.get(symbol, 100)

            # Add some random variation
            price = base_price * (1 + random.uniform(-0.02, 0.02))
            volume = random.uniform(1000, 10000)

            mock_data.append(
                {
                    "metadata_id": self.metadata_ids[symbol],
                    "timestamp_id": int(time.time()),  # Convert to timestamp_id
                    "price": round(price, 8),
                    "quote_volume24h": round(volume * 24, 8),  # Match YAML schema column name
                }
            )

        return mock_data

    def collect_from_exchanges(self) -> list[dict[str, Any]]:
        """Collect real market data from exchanges."""
        # TODO: Implement real exchange API calls
        # For now, using mock data
        self.logger.info_sync("Collecting market data from exchanges...")

        try:
            # Run async operation in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self.get_mock_market_data())
                return result
            finally:
                loop.close()
        except Exception as e:
            self.logger.error_sync(f"Error collecting market data: {e}")
            return []

    async def store_market_data_async(self, market_data: list[dict[str, Any]]) -> bool:
        """Store market data in the database using alphaloop-storage (async)."""
        if not market_data:
            return False

        try:
            # Use the table handler to store market data
            inserted_ids = await self.data_handler.insert_data(market_data)

            if inserted_ids is not None:
                self.logger.info_sync(
                    f"Stored {len(market_data)} market data records using infrastructure"
                )

                # Cache latest prices for quick access
                for data in market_data:
                    # Get symbol from metadata_id for caching
                    symbol = None
                    metadata_id = data.get("metadata_id")
                    if self.metadata_ids and metadata_id is not None:
                        for sym, mid in self.metadata_ids.items():
                            if mid == metadata_id:
                                symbol = sym
                                break
                    if symbol:
                        cache_key = f"latest_price_{symbol}"
                        await self.cache_manager.set_key(cache_key, data, ttl=300)

                return True
            else:
                self.logger.error_sync("Failed to store market data using infrastructure")
                return False

        except Exception as e:
            self.logger.error_sync(f"Error storing market data: {e}")
            return False

    def store_market_data(self, market_data: list[dict[str, Any]]) -> bool:
        """Store market data in the database (synchronous wrapper)."""
        if not market_data:
            return False

        try:
            # Run async operation in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self.store_market_data_async(market_data))
                return result
            finally:
                loop.close()
        except Exception as e:
            self.logger.error_sync(f"Error in store_market_data: {e}")
            return False

    def sync_with_cloud(self) -> bool:
        """Sync missing data with cloud infrastructure."""
        if not self.cloud_sync_enabled or not self.cloud_api_url:
            return False

        try:
            self.logger.info_sync("Syncing with cloud infrastructure...")
            # TODO: Implement cloud sync logic
            # - Check for missing data periods
            # - Request missing data from cloud API
            # - Store received data
            return True
        except Exception as e:
            self.logger.error_sync(f"Error syncing with cloud: {e}")
            return False

    def collect_and_store_market_data(self) -> bool:
        """Collect and store market data in one operation."""
        try:
            # Generate heartbeat
            asyncio.run(self.heartbeat_generator.generate_heartbeat())

            # Collect market data
            market_data = self.collect_from_exchanges()
            if market_data:
                return self.store_market_data(market_data)
            return False

        except Exception as e:
            self.logger.error_sync(f"Error in collect_and_store_market_data: {e}")
            return False

    def run_forever(self) -> None:
        """Main loop to collect and store market data continuously."""
        self.logger.info_sync(
            f"Starting Market Data Service (interval: {self.market_data_interval}s)"
        )

        last_sync_time = time.time()

        while True:
            try:
                # Collect and store market data
                self.collect_and_store_market_data()

                # Sync with cloud if needed
                current_time = time.time()
                if (
                    self.cloud_sync_enabled
                    and current_time - last_sync_time >= self.cloud_sync_interval
                ):
                    self.sync_with_cloud()
                    last_sync_time = current_time

                time.sleep(self.market_data_interval)

            except KeyboardInterrupt:
                self.logger.info_sync("Shutting down Market Data Service")
                break
            except Exception as e:
                self.logger.error_sync(f"Error in main loop: {e}")
                time.sleep(self.market_data_interval)

    def run_once(self) -> bool:
        """Run one collection cycle and return success status."""
        return self.collect_and_store_market_data()


if __name__ == "__main__":
    """Main entry point for the Market Data Service."""
    service = MarketDataService()
    service.run_forever()
