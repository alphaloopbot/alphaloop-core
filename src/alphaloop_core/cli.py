"""Command-line interface for AlphaLoop Core."""

import argparse
import sys
from typing import NoReturn

from .config import settings


def main() -> NoReturn:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AlphaLoop Core CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show service status")
    status_parser.add_argument(
        "--detailed", action="store_true", help="Show detailed status information"
    )

    # Config command
    config_parser = subparsers.add_parser("config", help="Show configuration")
    config_parser.add_argument("--key", type=str, help="Show specific configuration key")

    args = parser.parse_args()

    if args.command == "status":
        show_status(detailed=args.detailed)
    elif args.command == "config":
        show_config(key=args.key)
    else:
        parser.print_help()
        sys.exit(1)

    sys.exit(0)


def show_status(detailed: bool = False) -> None:
    """Show service status."""
    config = settings()

    if detailed:
        print("=== AlphaLoop Core Status ===")
        print(f"Environment: {config['ENVIRONMENT']}")
        print(f"Service URL: {config['SERVICE_URL']}")
        print(f"Log Level: {config['LOG_LEVEL']}")
        print(f"Database Host: {config['DB_HOST']}")
        print(f"Database Port: {config['DB_PORT']}")
        print(f"Database Name: {config['DB_NAME']}")
    else:
        print(f"Status: OK (Environment: {config['ENVIRONMENT']})")


def show_config(key: str | None = None) -> None:
    """Show configuration."""
    config = settings()

    if key:
        if key in config:
            print(f"{key}: {config[key]}")
        else:
            print(f"Configuration key '{key}' not found")
            print(f"Available keys: {', '.join(config.keys())}")
    else:
        print("=== AlphaLoop Core Configuration ===")
        for k, v in config.items():
            # Mask sensitive values
            if "password" in k.lower() or "key" in k.lower():
                v = "***" if v else "not set"
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
