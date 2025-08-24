#!/usr/bin/env python3
"""
CLI for AlphaLoop Storage database operations.

This provides the authoritative way to perform database operations
using alphaloop-storage as the single source of truth.
"""

import argparse
import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import alphaloop_storage
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from infrastructure.alphaloop_storage.core.database_setup import (
    setup_database_schemas_sync,
)

# Import logging
try:
    from alphaloop_logging import AlphaLoopLogger, LoggingConfig

    config = LoggingConfig(app_name="alphaloop-storage-cli")
    logger = AlphaLoopLogger(config)
except ImportError:
    # Fallback for development/testing
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("alphaloop-storage-cli")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="AlphaLoop Storage Database CLI")
    parser.add_argument("command", choices=["setup"], help="Command to execute")
    parser.add_argument(
        "--host",
        default=os.getenv("DB_HOST", "localhost"),
        help="Database host (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("DB_PORT", "5432")),
        help="Database port (default: 5432)",
    )
    parser.add_argument(
        "--user",
        default=os.getenv("DB_USER", "didac"),
        help="Database user (default: didac)",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("DB_PASSWORD", "your_secure_password"),
        help="Database password",
    )
    parser.add_argument(
        "--config",
        default="config/database_schema.yaml",
        help="Path to database schema YAML file",
    )

    args = parser.parse_args()

    if args.command == "setup":
        print("🗄️ Setting up database schemas using alphaloop-storage...")
        try:
            setup_database_schemas_sync(
                host=args.host,
                port=args.port,
                user=args.user,
                password=args.password,
                config_path=args.config,
            )
            print("✅ Database setup completed successfully!")
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
