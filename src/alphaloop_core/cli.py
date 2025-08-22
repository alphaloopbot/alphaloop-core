"""Command-line interface for AlphaLoop Core."""

import argparse
import re
import sys
from typing import NoReturn
from urllib.parse import urlsplit, urlunsplit

from .config import settings

SENSITIVE_KEY_SUBSTRINGS = (
    "password",
    "key",
    "secret",
    "token",
    "apikey",
    "access_key",
    "private_key",
)


def _is_sensitive_key(key: str) -> bool:
    k = key.lower()
    return any(s in k for s in SENSITIVE_KEY_SUBSTRINGS)


def _mask_dsn(value: str) -> str:
    try:
        parts = urlsplit(value)
        if "@" not in parts.netloc or ":" not in parts.netloc.split("@", 1)[0]:
            return value  # no credentials present
        userinfo, host = parts.netloc.split("@", 1)
        user = userinfo.split(":", 1)[0]
        masked_netloc = f"{user}:***@{host}"
        return urlunsplit((parts.scheme, masked_netloc, parts.path, parts.query, parts.fragment))
    except Exception:
        # Conservative fallback: redact anything between : and @
        return re.sub(r":[^@]+@", ":***@", value)


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
            # Mask sensitive values and DSNs containing credentials
            if _is_sensitive_key(k):
                v = "***" if v else "not set"
            elif k.upper() in {"DATABASE_URL"}:
                v = _mask_dsn(v)
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
