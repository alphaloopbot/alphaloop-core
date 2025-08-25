"""
Heartbeat checker for service monitoring.

This module provides functionality to check and validate heartbeat files created by
services. The heartbeat checker is essential for monitoring systems to detect when
services become unresponsive or fail.

The checker reads heartbeat files and determines if services are healthy based on
the freshness of their heartbeat data and the configured timeout thresholds.

Key Features:
- Configurable timeout thresholds
- Multiple service monitoring
- Graceful error handling
- Detailed health status reporting
- Process validation capabilities
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

from ..config.settings import HeartbeatSettings
from ..utils.file_utils import get_heartbeat_file_path
from ..utils.time_utils import get_current_timestamp

logger = logging.getLogger(__name__)


class HeartbeatChecker:
    """
    Checks heartbeat files to determine service health status.

    This class is responsible for monitoring heartbeat files created by services
    and determining whether those services are healthy based on the freshness
    of their heartbeat data.

    The checker reads JSON heartbeat files and compares their timestamps against
    configured timeout thresholds to determine if services are responding normally
    or if they may have failed or become unresponsive.

    Key Features:
    - Configurable timeout thresholds
    - Multiple service monitoring
    - Process validation (optional)
    - Detailed health status reporting
    - Graceful error handling

    Usage:
        checker = HeartbeatChecker(settings=my_settings)
        status = await checker.check_service_health("my-service")
    """

    def __init__(self, settings: HeartbeatSettings | None = None) -> None:
        """
        Initialize the heartbeat checker.

        Creates a new heartbeat checker with the specified settings. The checker
        will use these settings to determine timeout thresholds and behavior.

        Args:
            settings: Configuration settings for heartbeat checking behavior.
                     If None, default settings will be used.

        Example:
            >>> checker = HeartbeatChecker(settings=my_settings)
            >>> checker = HeartbeatChecker()  # Uses default settings
        """
        self.settings = settings or HeartbeatSettings()

    def _is_process_running(self, pid: int) -> bool:
        """
        Check if a process with the given PID is still running.

        This method validates that a process is actually running by sending
        a signal 0 (which doesn't actually send a signal but checks if the
        process exists). This helps distinguish between a stopped service
        and a service that has crashed or been killed.

        Args:
            pid: The process ID to check

        Returns:
            True if the process is running, False otherwise

        Example:
            >>> checker._is_process_running(12345)
            True
            >>> checker._is_process_running(99999)
            False
        """
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def _handle_dead_process(self, service_name: str, pid: int) -> None:
        """
        Handle cleanup when a dead process is detected.

        This method is called when a process is found to be dead during
        heartbeat checking. It performs any necessary cleanup operations
        and logs the event for monitoring purposes.

        Args:
            service_name: Name of the service that has died
            pid: Process ID of the dead process

        Example:
            >>> checker._handle_dead_process("worker-service", 12345)
            # Logs the event and performs cleanup
        """
        logger.warning(f"Process {pid} for service {service_name} is dead")

    async def check_service_health(
        self, service_name: str, timeout_seconds: int | None = None
    ) -> dict[str, Any]:
        """
        Check the health status of a specific service.

        Reads the heartbeat file for the specified service and determines
        if the service is healthy based on the freshness of its heartbeat
        data and the configured timeout threshold.

        The health check considers:
        - Whether the heartbeat file exists
        - How recent the heartbeat timestamp is
        - Whether the service process is still running (if PID is available)
        - Any errors in the heartbeat data

        Args:
            service_name: Name of the service to check
            timeout_seconds: Override the default timeout threshold in seconds.
                           If None, uses the timeout from settings.

        Returns:
            Dictionary containing health status information:
            - healthy: Boolean indicating if service is healthy
            - last_heartbeat: Timestamp of last heartbeat (or None)
            - age_seconds: Age of last heartbeat in seconds (or None)
            - error: Error message if health check failed (or None)
            - details: Additional health information

        Raises:
            FileNotFoundError: If heartbeat file doesn't exist
            json.JSONDecodeError: If heartbeat file is corrupted
            ValueError: If heartbeat data is invalid

        Example:
            >>> status = await checker.check_service_health("api-service")
            >>> print(status["healthy"])
            True
            >>> print(status["age_seconds"])
            15
        """
        timeout = timeout_seconds or self.settings.default_timeout_seconds
        heartbeat_file = get_heartbeat_file_path(
            service_name, Path(self.settings.heartbeat_directory)
        )

        if not heartbeat_file.exists():
            return {
                "healthy": False,
                "last_heartbeat": None,
                "age_seconds": None,
                "error": f"Heartbeat file not found: {heartbeat_file}",
                "details": {"file_exists": False},
            }

        try:
            with open(heartbeat_file, encoding="utf-8") as f:
                heartbeat_data = json.load(f)

            last_heartbeat = heartbeat_data.get("timestamp")
            if not last_heartbeat:
                return {
                    "healthy": False,
                    "last_heartbeat": None,
                    "age_seconds": None,
                    "error": "No timestamp in heartbeat data",
                    "details": {"heartbeat_data": heartbeat_data},
                }

            current_time = get_current_timestamp()
            age_seconds = current_time - last_heartbeat

            # Check if heartbeat is too old
            if age_seconds > timeout:
                return {
                    "healthy": False,
                    "last_heartbeat": last_heartbeat,
                    "age_seconds": age_seconds,
                    "error": f"Heartbeat too old: {age_seconds}s > {timeout}s",
                    "details": {"timeout_seconds": timeout},
                }

            # Check if process is still running (if PID is available)
            pid = heartbeat_data.get("pid")
            if pid is not None and not self._is_process_running(pid):
                self._handle_dead_process(service_name, pid)
                return {
                    "healthy": False,
                    "last_heartbeat": last_heartbeat,
                    "age_seconds": age_seconds,
                    "error": f"Process {pid} is dead",
                    "details": {"pid": pid, "process_running": False},
                }

            return {
                "healthy": True,
                "last_heartbeat": last_heartbeat,
                "age_seconds": age_seconds,
                "error": None,
                "details": {
                    "service_name": heartbeat_data.get("service_name"),
                    "version": heartbeat_data.get("version"),
                    "status": heartbeat_data.get("status"),
                    "pid": pid,
                },
            }

        except json.JSONDecodeError as e:
            return {
                "healthy": False,
                "last_heartbeat": None,
                "age_seconds": None,
                "error": f"Invalid JSON in heartbeat file: {e}",
                "details": {"file_path": str(heartbeat_file)},
            }
        except Exception as e:
            return {
                "healthy": False,
                "last_heartbeat": None,
                "age_seconds": None,
                "error": f"Error checking heartbeat: {e}",
                "details": {"file_path": str(heartbeat_file)},
            }

    async def check_all_services(self, service_names: list[str]) -> dict[str, Any]:
        """
        Check the health status of multiple services.

        Performs health checks on all specified services and returns a summary
        of their collective health status. This is useful for monitoring systems
        that need to track multiple services simultaneously.

        Args:
            service_names: List of service names to check

        Returns:
            Dictionary containing overall health status:
            - all_healthy: Boolean indicating if all services are healthy
            - healthy_count: Number of healthy services
            - total_count: Total number of services checked
            - services: Dictionary mapping service names to their health status
            - summary: Summary of health check results

        Example:
            >>> services = ["api-service", "worker-service", "db-service"]
            >>> status = await checker.check_all_services(services)
            >>> print(status["all_healthy"])
            False
            >>> print(status["healthy_count"])
            2
        """
        results = {}
        healthy_count = 0

        for service_name in service_names:
            health_status = await self.check_service_health(service_name)
            results[service_name] = health_status
            if health_status["healthy"]:
                healthy_count += 1

        all_healthy = healthy_count == len(service_names)

        return {
            "all_healthy": all_healthy,
            "healthy_count": healthy_count,
            "total_count": len(service_names),
            "services": results,
            "summary": {
                "healthy_services": [name for name, status in results.items() if status["healthy"]],
                "unhealthy_services": [
                    name for name, status in results.items() if not status["healthy"]
                ],
            },
        }
