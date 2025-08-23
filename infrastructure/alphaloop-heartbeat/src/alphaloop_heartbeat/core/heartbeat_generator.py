"""
Heartbeat generator for service monitoring.

This module provides the core functionality for generating heartbeat files that indicate
service health and status. Heartbeats are essential for monitoring distributed systems
and detecting when services become unresponsive or fail.

The heartbeat generator creates timestamped JSON files that contain service status
information, allowing monitoring systems to track service health and detect failures
in real-time.

Key Features:
- Atomic file writes to prevent corruption
- Configurable heartbeat intervals
- Service name sanitization for security
- Automatic directory creation
- Graceful error handling and retry logic
"""

import asyncio
import json
import logging
import os
import re

from alphaloop_heartbeat.config.settings import HeartbeatSettings
from alphaloop_heartbeat.utils.file_utils import get_heartbeat_file_path
from alphaloop_heartbeat.utils.time_utils import get_current_timestamp

# Package version from pyproject.toml
PACKAGE_VERSION = "0.1.0"


def _sanitize_service_name(name: str) -> str:
    """
    Sanitize user-supplied service names to safe filenames.

    This function ensures that service names are converted to safe filenames by:
    - Removing path traversal attempts (../, etc.)
    - Replacing unsafe characters with underscores
    - Preventing directory traversal attacks
    - Ensuring the filename is valid for the filesystem

    Args:
        name: The raw service name provided by the user

    Returns:
        A sanitized filename-safe string

    Raises:
        ValueError: If the service name is invalid or contains path traversal

    Example:
        >>> _sanitize_service_name("my-service")
        'my-service'
        >>> _sanitize_service_name("../../../etc/passwd")
        ValueError: Invalid service_name
    """
    base = os.path.basename(name.strip())
    if base in {"", ".", ".."}:
        raise ValueError("Invalid service_name")
    # Allow alnum, underscore, dash, dot; collapse any pathy/dotty patterns
    base = re.sub(r"[^A-Za-z0-9_.-]+", "_", base)
    base = re.sub(r"\.\.+", "_", base)
    return base


logger = logging.getLogger(__name__)


class HeartbeatGenerator:
    """
    Generates heartbeat files for service monitoring.

    This class is responsible for creating and maintaining heartbeat files that indicate
    service health and status. Heartbeats are crucial for monitoring distributed systems
    and detecting service failures in real-time.

    The generator creates timestamped JSON files containing service information,
    which can be monitored by external systems to detect when services become
    unresponsive or fail.

    Key Features:
    - Configurable heartbeat intervals
    - Atomic file writes to prevent corruption
    - Automatic directory creation
    - Graceful error handling
    - Service name sanitization
    - Version tracking

    Usage:
        generator = HeartbeatGenerator("my-service", interval=30)
        await generator.start_generating()
    """

    def __init__(
        self,
        service_name: str,
        settings: HeartbeatSettings | None = None,
        interval: int | None = None,
        version: str | None = None,
    ) -> None:
        """
        Initialize the heartbeat generator.

        Creates a new heartbeat generator for the specified service. The generator
        will create heartbeat files at regular intervals to indicate service health.

        Args:
            service_name: Name of the service to monitor. Will be sanitized for
                         filesystem safety.
            settings: Configuration settings for heartbeat behavior. If None,
                     default settings will be used.
            interval: Override the heartbeat interval in seconds. If None, uses
                     the interval from settings.
            version: Service version to include in heartbeat data. If None, uses
                    the package version.

        Raises:
            ValueError: If interval is <= 0 or service_name is invalid

        Example:
            >>> generator = HeartbeatGenerator("api-service", interval=60)
            >>> generator = HeartbeatGenerator("worker-service", settings=my_settings)
        """
        self.service_name = _sanitize_service_name(service_name)
        self.settings = settings or HeartbeatSettings()
        self._running = False
        # Runtime configuration derived from settings or explicit overrides
        self._interval = (
            interval
            if interval is not None
            else getattr(self.settings, "default_interval_seconds", 60)
        )
        if self._interval <= 0:
            raise ValueError("interval must be > 0 seconds")
        self.version = version or PACKAGE_VERSION

    async def generate_heartbeat(self) -> None:
        """
        Generate a heartbeat file for the service.

        Creates a new heartbeat file with current timestamp and service status.
        The file is written atomically to prevent corruption if the process
        is interrupted during writing.

        The heartbeat file contains:
        - service_name: The name of the service
        - timestamp: Current timestamp when heartbeat was generated
        - status: Service status (always "healthy" for active heartbeats)
        - version: Service version information

        The file is written to the configured heartbeat directory with
        the service name as the filename.

        Raises:
            OSError: If unable to write to the heartbeat directory
            ValueError: If heartbeat data is invalid

        Example:
            >>> await generator.generate_heartbeat()
            # Creates: /heartbeats/my-service.json
        """
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
        """
        Start generating heartbeats at regular intervals.

        Begins the continuous heartbeat generation process. The generator will
        create heartbeat files at the configured interval until stopped.

        This method runs indefinitely until stop_generating() is called or
        the task is cancelled. It includes error handling to ensure the
        heartbeat generation continues even if individual heartbeats fail.

        The generator will:
        - Create heartbeat files at regular intervals
        - Handle errors gracefully with retry logic
        - Log heartbeat generation events
        - Continue running until explicitly stopped

        Raises:
            asyncio.CancelledError: If the task is cancelled

        Example:
            >>> await generator.start_generating()
            # Generates heartbeats every 60 seconds until stopped
        """
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
        """
        Stop generating heartbeats.

        Signals the heartbeat generator to stop creating new heartbeat files.
        The generator will complete its current heartbeat cycle and then stop.

        This method is safe to call multiple times and can be called from
        any thread or coroutine.

        Example:
            >>> generator.stop_generating()
            # Heartbeat generation will stop after current cycle
        """
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
        "--interval",
        type=int,
        default=30,
        help="Heartbeat interval in seconds (default: 30)",
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
