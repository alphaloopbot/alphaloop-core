#!/usr/bin/env python3
"""
AlphaLoop Market Data Service

This is a thin wrapper that imports and runs the market data service from alphaloop-core.
All business logic is contained in alphaloop-core.services.market_data.
"""

from alphaloop_core.services.market_data import MarketDataService


def main():
    """Main entry point - just import and run the service from alphaloop-core."""
    service = MarketDataService()
    service.run_forever()


if __name__ == "__main__":
    main()
