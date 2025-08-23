#!/usr/bin/env python3
"""
AlphaLoop Market Data Service

This service provides market data API endpoints and collects market data.
"""

import logging
import os
from datetime import datetime

import psycopg2
from flask import Flask, jsonify, request
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


class MarketDataService:
    """Market data service with API endpoints."""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.market_data_interval = int(os.getenv("MARKET_DATA_INTERVAL", 10))
        self.market_database = os.getenv("MARKET_DATABASE", "alphaloop_market")
        self.cloud_api_url = os.getenv("CLOUD_API_URL")
        self.cloud_sync_enabled = os.getenv("CLOUD_SYNC_ENABLED", "true").lower() == "true"

    def get_db_connection(self):
        """Get database connection."""
        try:
            conn = psycopg2.connect(self.database_url)
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return None

    def create_tables(self):
        """Create necessary tables if they don't exist."""
        conn = self.get_db_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()

            # Create market data table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS market_data (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                price DECIMAL(20, 8) NOT NULL,
                volume DECIMAL(20, 8),
                timestamp TIMESTAMP NOT NULL,
                source VARCHAR(50) DEFAULT 'local',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            cursor.execute(create_table_sql)

            # Create index on symbol and timestamp
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp
            ON market_data(symbol, timestamp);
            """)

            conn.commit()
            cursor.close()
            conn.close()

            logger.info("Market data tables created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            return False

    def get_mock_market_data(self):
        """Generate mock market data for testing."""
        import random

        symbols = ["BTC/USDT", "ETH/USDT", "ADA/USDT", "DOT/USDT"]
        mock_data = []

        for symbol in symbols:
            # Generate realistic price movements
            base_price = {"BTC/USDT": 45000, "ETH/USDT": 3000, "ADA/USDT": 0.5, "DOT/USDT": 20}.get(
                symbol, 100
            )

            # Add some random variation
            price = base_price * (1 + random.uniform(-0.05, 0.05))
            volume = random.uniform(1000, 10000)

            mock_data.append(
                {
                    "symbol": symbol,
                    "price": round(price, 8),
                    "volume": round(volume, 8),
                    "timestamp": datetime.now(),
                    "source": "mock",
                }
            )

        return mock_data

    def store_market_data(self, market_data):
        """Store market data in the database."""
        conn = self.get_db_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()

            for data in market_data:
                insert_sql = """
                INSERT INTO market_data (symbol, price, volume, timestamp, source)
                VALUES (%s, %s, %s, %s, %s)
                """

                cursor.execute(
                    insert_sql,
                    (
                        data["symbol"],
                        data["price"],
                        data["volume"],
                        data["timestamp"],
                        data["source"],
                    ),
                )

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"Stored {len(market_data)} market data records")
            return True

        except Exception as e:
            logger.error(f"Error storing market data: {e}")
            return False

    def get_latest_prices(self, symbol=None):
        """Get latest prices from database."""
        conn = self.get_db_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            if symbol:
                query = """
                SELECT symbol, price, volume, timestamp, source
                FROM market_data
                WHERE symbol = %s
                ORDER BY timestamp DESC
                LIMIT 1
                """
                cursor.execute(query, (symbol,))
            else:
                query = """
                SELECT DISTINCT ON (symbol) symbol, price, volume, timestamp, source
                FROM market_data
                ORDER BY symbol, timestamp DESC
                """
                cursor.execute(query)

            results = cursor.fetchall()
            cursor.close()
            conn.close()

            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Error getting latest prices: {e}")
            return []


# Global service instance
market_service = MarketDataService()


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        conn = market_service.get_db_connection()
        if conn:
            conn.close()
            db_status = "healthy"
        else:
            db_status = "unhealthy"

        return jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "database": db_status,
                "service": "alphaloop-market-data",
            }
        ), 200
    except Exception as e:
        return jsonify(
            {"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}
        ), 500


@app.route("/api/v1/status", methods=["GET"])
def status():
    """Service status endpoint."""
    return jsonify(
        {
            "service": "alphaloop-market-data",
            "version": "1.0.0",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "database_url": market_service.database_url is not None,
            "cloud_sync_enabled": market_service.cloud_sync_enabled,
        }
    ), 200


@app.route("/api/v1/prices", methods=["GET"])
def get_prices():
    """Get latest prices."""
    symbol = request.args.get("symbol")
    prices = market_service.get_latest_prices(symbol)

    return jsonify(
        {"prices": prices, "count": len(prices), "timestamp": datetime.now().isoformat()}
    ), 200


@app.route("/api/v1/collect", methods=["POST"])
def collect_market_data():
    """Collect and store market data."""
    try:
        # Generate mock data
        market_data = market_service.get_mock_market_data()

        # Store in database
        success = market_service.store_market_data(market_data)

        if success:
            return jsonify(
                {
                    "status": "success",
                    "collected": len(market_data),
                    "timestamp": datetime.now().isoformat(),
                }
            ), 200
        else:
            return jsonify(
                {
                    "status": "error",
                    "message": "Failed to store market data",
                    "timestamp": datetime.now().isoformat(),
                }
            ), 500

    except Exception as e:
        return jsonify(
            {"status": "error", "message": str(e), "timestamp": datetime.now().isoformat()}
        ), 500


def main():
    """Main entry point."""
    logger.info("Starting AlphaLoop Market Data Service")

    # Create tables
    market_service.create_tables()

    # Start Flask app
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
