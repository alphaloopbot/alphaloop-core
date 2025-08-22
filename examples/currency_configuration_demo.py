#!/usr/bin/env python3
"""
Demonstration of configurable currency support in AlphaLoop Core.

This script shows how the default currency can be configured and how
MarketData entities use the configured default currency.
"""

import os
from uuid import uuid4

from alphaloop_core.config import get_default_currency
from alphaloop_core.domain.entities.market_data import MarketData
from alphaloop_core.shared.types.enums import Currency


def demo_default_currency():
    """Demonstrate the default currency configuration."""
    print("🪙 Currency Configuration Demo\n")

    # Show current default currency
    default_currency = get_default_currency()
    print(f"📊 Current default currency: {default_currency.value}")

    # Create MarketData without specifying currency (uses default)
    market_data_default = MarketData(
        metadata_id="BTC-USDT",
        timestamp_id=1642780800,
        price=42000.50,
        quote_volume24h=1500000.0,
        entity_id=uuid4(),
    )

    print(f"💰 MarketData with default currency: {market_data_default.price.currency.value}")
    print(f"💲 Price: {market_data_default.price.value} {market_data_default.price.currency.value}")

    # Create MarketData with explicit currency
    market_data_explicit = MarketData(
        metadata_id="ETH-BTC",
        timestamp_id=1642780800,
        price=0.075,
        quote_volume24h=850.0,
        currency=Currency.BTC,
        entity_id=uuid4(),
    )

    print(f"💰 MarketData with explicit currency: {market_data_explicit.price.currency.value}")
    print(
        f"💲 Price: {market_data_explicit.price.value} {market_data_explicit.price.currency.value}"
    )

    # Show serialization includes currency
    print("\n📄 Serialized data includes currency:")
    data_dict = market_data_default.to_dict()
    print(f"   Currency in serialized data: {data_dict['currency']}")

    return market_data_default, market_data_explicit


def demo_currency_override():
    """Demonstrate overriding the default currency via environment."""
    print("\n🔧 Currency Override Demo\n")

    # Temporarily override the default currency
    original_currency = os.getenv("DEFAULT_CURRENCY")

    try:
        # Set new default currency
        os.environ["DEFAULT_CURRENCY"] = "BTC"

        # Clear the settings cache to pick up new environment
        from alphaloop_core.config import settings

        settings.cache_clear()

        new_default = get_default_currency()
        print(f"🔄 New default currency: {new_default.value}")

        # Create MarketData with new default
        market_data_btc = MarketData(
            metadata_id="ETH-BTC",
            timestamp_id=1642780800,
            price=0.075,
            quote_volume24h=850.0,
            entity_id=uuid4(),
        )

        print(f"💰 MarketData now uses: {market_data_btc.price.currency.value}")

    finally:
        # Restore original currency
        if original_currency:
            os.environ["DEFAULT_CURRENCY"] = original_currency
        else:
            os.environ.pop("DEFAULT_CURRENCY", None)

        # Clear cache again to restore original
        settings.cache_clear()

    return market_data_btc


def demo_deserialization():
    """Demonstrate currency handling in deserialization."""
    print("\n📦 Deserialization Demo\n")

    # Create sample data dict with currency
    data_with_currency = {
        "id": str(uuid4()),
        "metadata_id": "BTC-USDT",
        "timestamp_id": 1642780800,
        "price": 42000.50,
        "quote_volume24h": 1500000.0,
        "currency": "EUR",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }

    # Create MarketData from dict
    market_data_from_dict = MarketData.from_dict(data_with_currency)
    print(f"💰 Deserialized with currency: {market_data_from_dict.price.currency.value}")

    # Create sample data dict without currency (should use default)
    data_without_currency = data_with_currency.copy()
    del data_without_currency["currency"]

    market_data_default = MarketData.from_dict(data_without_currency)
    print(
        f"💰 Deserialized without currency (uses default): {market_data_default.price.currency.value}"
    )

    return market_data_from_dict, market_data_default


def main():
    """Run all demonstrations."""
    print("🚀 AlphaLoop Core - Currency Configuration Demonstration\n")
    print("=" * 60)

    # Demo 1: Basic currency configuration
    demo_default_currency()

    # Demo 2: Environment override
    demo_currency_override()

    # Demo 3: Deserialization
    demo_deserialization()

    print("\n" + "=" * 60)
    print("✅ All currency demonstrations completed!")
    print("\n💡 Key Points:")
    print("   • Default currency is USDT (configurable via DEFAULT_CURRENCY env var)")
    print("   • MarketData entities can override the default currency when needed")
    print("   • Currency information is preserved in serialization/deserialization")
    print("   • Invalid currency values fall back to USDT safely")


if __name__ == "__main__":
    main()
