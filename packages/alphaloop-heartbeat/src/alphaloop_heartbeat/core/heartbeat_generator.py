"""Heartbeat generator for service monitoring."""

import asyncio
import json
import logging
import os
import re

from alphaloop_heartbeat.config.settings import HeartbeatSettings
from alphaloop_heartbeat.utils.file_utils import get_heartbeat_file_path
from alphaloop_heartbeat.utils.time_utils import get_current_timestamp


def _sanitize_service_name(name: str) -> str:
    """Sanitize user-supplied service names to safe filenames."""
    base = os.path.basename(name.strip())
    if base in {"", ".", ".."}:
        raise ValueError("Invalid service_name")
    # Allow alnum, underscore, dash, dot; collapse any pathy/dotty patterns
    base = re.sub(r"[^A-Za-z0-9_.-]+", "_", base)
    base = re.sub(r"\.\.+", "_", base)
    return base


logger = logging.getLogger(__name__)


class HeartbeatGenerator:
    """Generates heartbeat files for service monitoring."""

    def __init__(
        self,
        service_name: str,
        settings: HeartbeatSettings | None = None,
        interval: int | None = None,
        version: str | None = None,
    ) -> None:
        """Initialize the heartbeat generator."""
        self.service_name = _sanitize_service_name(service_name)
        self.settings = settings or HeartbeatSettings()
        self._running = False
        # Runtime configuration derived from settings or explicit overrides
        self._interval = (
            interval
            if interval is not None
            else getattr(self.settings, "default_interval_seconds", 60)
        )
        self.version = version or "1.0.0"

    async def generate_heartbeat(self) -> None:
        """Generate a heartbeat file for the service."""
        import os
        from pathlib import Path

        heartbeat_data = {
            "service_name": self.service_name,
            "timestamp": get_current_timestamp(),
            "status": "healthy",
            "version": self.version,
        }

        heartbeat_file = get_heartbeat_file_path(
            self.service_name, Path(self.settings.heartbeat_directory)
        )
        heartbeat_file.parent.mkdir(parents=True, exist_ok=True)

        # Atomic write: write to tmp and replace
        tmp_file = heartbeat_file.with_suffix(heartbeat_file.suffix + ".tmp")
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(heartbeat_data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_file, heartbeat_file)

        logger.debug("Heartbeat generated for %s", self.service_name)

    async def start_generating(self) -> None:
        """Start generating heartbeats at regular intervals."""
        self._running = True
        logger.info(f"Starting heartbeat generation for {self.service_name}")

        while self._running:
            try:
                await self.generate_heartbeat()
                await asyncio.sleep(self._interval)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"Error during heartbeat generation: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    def stop_generating(self) -> None:
        """Stop generating heartbeats."""
        self._running = False
        logger.info(f"Stopped heartbeat generation for {self.service_name}")


async def main() -> None:
    """Main entry point for the heartbeat generator."""
    import argparse
    import signal
    import sys

    parser = argparse.ArgumentParser(description="Generate heartbeats for service monitoring")
    parser.add_argument("service_name", help="Name of the service to monitor")
    parser.add_argument(
        "--interval", type=int, default=30, help="Heartbeat interval in seconds (default: 30)"
    )
    parser.add_argument("--version", default="1.0.0", help="Service version (default: 1.0.0)")

    args = parser.parse_args()

    # Configure settings
    settings = HeartbeatSettings()

    # Create generator with explicit interval/version overrides
    generator = HeartbeatGenerator(
        args.service_name, settings, interval=args.interval, version=args.version
    )

    # Set up signal handlers
    def signal_handler(signum: int, frame: object) -> None:
        logger.info("Received shutdown signal")
        generator.stop_generating()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await generator.start_generating()
    except KeyboardInterrupt:
        logger.info("Heartbeat generation interrupted")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
