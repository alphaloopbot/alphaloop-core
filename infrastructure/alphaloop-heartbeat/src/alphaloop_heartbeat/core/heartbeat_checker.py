"""Heartbeat checker for monitoring heartbeat files and detecting stale services."""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import psutil

from ..config.settings import HeartbeatSettings
from ..utils.file_utils import get_heartbeat_directory
from ..utils.time_utils import get_current_timestamp


class HeartbeatChecker:
    """Monitors heartbeat files and detects stale services."""

    def __init__(self, settings: HeartbeatSettings | None = None) -> None:
        """Initialize the heartbeat checker."""
        self._settings = settings or HeartbeatSettings()
        self._heartbeat_dir = get_heartbeat_directory()
        self._running = False
        self._check_interval = self._settings.check_interval_seconds

    async def start_monitoring(self) -> None:
        """Start monitoring heartbeat files."""
        self._running = True
        print(f"Starting heartbeat monitoring in {self._heartbeat_dir}")

        while self._running:
            try:
                await self._check_all_heartbeats()
                await asyncio.sleep(self._check_interval)
            except Exception as e:
                print(f"Error during heartbeat monitoring: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def stop_monitoring(self) -> None:
        """Stop monitoring heartbeat files."""
        self._running = False
        print("Stopping heartbeat monitoring")

    async def _check_all_heartbeats(self) -> None:
        """Check all heartbeat files in the directory."""
        if not self._heartbeat_dir.exists():
            return

        heartbeat_files = list(self._heartbeat_dir.glob("*.json"))

        for heartbeat_file in heartbeat_files:
            try:
                await self._check_single_heartbeat(heartbeat_file)
            except Exception as e:
                print(f"Error checking heartbeat file {heartbeat_file}: {e}")

    async def _check_single_heartbeat(self, heartbeat_file: Path) -> None:
        """Check a single heartbeat file."""
        try:
            with open(heartbeat_file) as f:
                heartbeat_data = json.load(f)

            service_name = heartbeat_data.get("service_name", heartbeat_file.stem)
            last_heartbeat = heartbeat_data.get("timestamp")
            process_id = heartbeat_data.get("process_id")
            expected_interval = heartbeat_data.get(
                "interval_seconds", self._settings.default_interval_seconds
            )

            if not last_heartbeat:
                print(f"Warning: No timestamp found in heartbeat file {heartbeat_file}")
                return

            # Parse timestamp
            try:
                last_heartbeat_time = datetime.fromisoformat(last_heartbeat)
            except ValueError:
                print(f"Warning: Invalid timestamp format in {heartbeat_file}")
                return

            # Check if heartbeat is stale
            current_time = datetime.now()
            time_since_last_heartbeat = current_time - last_heartbeat_time
            stale_threshold = timedelta(seconds=expected_interval * self._settings.stale_multiplier)

            if time_since_last_heartbeat > stale_threshold:
                await self._handle_stale_heartbeat(
                    service_name, heartbeat_file, last_heartbeat_time, process_id
                )
            else:
                # Heartbeat is fresh, check if process is still running
                if process_id and not self._is_process_running(process_id):
                    await self._handle_dead_process(service_name, heartbeat_file, process_id)

        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in heartbeat file {heartbeat_file}")
        except Exception as e:
            print(f"Error processing heartbeat file {heartbeat_file}: {e}")

    async def _handle_stale_heartbeat(
        self,
        service_name: str,
        heartbeat_file: Path,
        last_heartbeat: datetime,
        process_id: int | None,
    ) -> None:
        """Handle a stale heartbeat."""
        current_time = datetime.now()
        time_since_last_heartbeat = current_time - last_heartbeat

        print(f"⚠️  STALE HEARTBEAT: {service_name}")
        print(f"   Last heartbeat: {last_heartbeat.isoformat()}")
        print(f"   Time since last: {time_since_last_heartbeat}")
        print(f"   Process ID: {process_id}")
        print(f"   File: {heartbeat_file}")

        # Check if process is still running
        if process_id and self._is_process_running(process_id):
            print(f"   Process {process_id} is still running - service may be unresponsive")
        else:
            print(f"   Process {process_id} is not running - service has stopped")

        # Trigger alert if configured
        if self._settings.enable_alerts:
            await self._send_alert(
                service_name,
                "stale_heartbeat",
                {
                    "last_heartbeat": last_heartbeat.isoformat(),
                    "time_since_last": str(time_since_last_heartbeat),
                    "process_id": process_id,
                },
            )

    async def _handle_dead_process(
        self, service_name: str, heartbeat_file: Path, process_id: int
    ) -> None:
        """Handle a dead process."""
        print(f"💀 DEAD PROCESS: {service_name}")
        print(f"   Process ID: {process_id}")
        print(f"   File: {heartbeat_file}")

        # Clean up heartbeat file
        try:
            heartbeat_file.unlink()
            print(f"   Cleaned up heartbeat file: {heartbeat_file}")
        except Exception as e:
            print(f"   Failed to clean up heartbeat file: {e}")

        # Trigger alert if configured
        if self._settings.enable_alerts:
            await self._send_alert(
                service_name,
                "dead_process",
                {
                    "process_id": process_id,
                },
            )

    def _is_process_running(self, process_id: int) -> bool:
        """Check if a process is still running."""
        try:
            process = psutil.Process(process_id)
            return process.is_running()
        except psutil.NoSuchProcess:
            return False
        except Exception:
            return False

    async def _send_alert(
        self, service_name: str, alert_type: str, details: dict[str, Any]
    ) -> None:
        """Send an alert about a service issue."""
        # This would integrate with your alerting system (email, Slack, etc.)
        alert = {
            "timestamp": get_current_timestamp(),
            "service_name": service_name,
            "alert_type": alert_type,
            "details": details,
        }

        print(f"🚨 ALERT: {alert}")
        # TODO: Implement actual alert sending logic

    async def get_heartbeat_status(self) -> dict[str, Any]:
        """Get the current status of all heartbeats."""
        status = {
            "timestamp": get_current_timestamp(),
            "heartbeat_directory": str(self._heartbeat_dir),
            "services": [],
            "summary": {
                "total_services": 0,
                "healthy_services": 0,
                "stale_services": 0,
                "dead_services": 0,
            },
        }

        if not self._heartbeat_dir.exists():
            return status

        heartbeat_files = list(self._heartbeat_dir.glob("*.json"))
        status["summary"]["total_services"] = len(heartbeat_files)

        for heartbeat_file in heartbeat_files:
            try:
                service_status = await self._get_service_status(heartbeat_file)
                status["services"].append(service_status)

                if service_status["status"] == "healthy":
                    status["summary"]["healthy_services"] += 1
                elif service_status["status"] == "stale":
                    status["summary"]["stale_services"] += 1
                elif service_status["status"] == "dead":
                    status["summary"]["dead_services"] += 1

            except Exception as e:
                print(f"Error getting status for {heartbeat_file}: {e}")

        return status

    async def _get_service_status(self, heartbeat_file: Path) -> dict[str, Any]:
        """Get the status of a single service."""
        try:
            with open(heartbeat_file) as f:
                heartbeat_data = json.load(f)

            service_name = heartbeat_data.get("service_name", heartbeat_file.stem)
            last_heartbeat = heartbeat_data.get("timestamp")
            process_id = heartbeat_data.get("process_id")
            expected_interval = heartbeat_data.get(
                "interval_seconds", self._settings.default_interval_seconds
            )

            if not last_heartbeat:
                return {
                    "service_name": service_name,
                    "status": "unknown",
                    "error": "No timestamp found",
                }

            last_heartbeat_time = datetime.fromisoformat(last_heartbeat)
            current_time = datetime.now()
            time_since_last_heartbeat = current_time - last_heartbeat_time
            stale_threshold = timedelta(seconds=expected_interval * self._settings.stale_multiplier)

            status = {
                "service_name": service_name,
                "last_heartbeat": last_heartbeat,
                "time_since_last": str(time_since_last_heartbeat),
                "process_id": process_id,
                "expected_interval": expected_interval,
            }

            if time_since_last_heartbeat > stale_threshold:
                status["status"] = "stale"
            elif process_id and not self._is_process_running(process_id):
                status["status"] = "dead"
            else:
                status["status"] = "healthy"

            return status

        except Exception as e:
            return {
                "service_name": heartbeat_file.stem,
                "status": "error",
                "error": str(e),
            }


async def main() -> None:
    """Main function for the heartbeat checker."""
    import argparse

    parser = argparse.ArgumentParser(description="AlphaLoop Heartbeat Checker")
    parser.add_argument("--config", "-c", type=str, help="Path to configuration file")
    parser.add_argument(
        "--status",
        "-s",
        action="store_true",
        help="Show current heartbeat status and exit",
    )
    parser.add_argument("--interval", "-i", type=int, help="Check interval in seconds")

    args = parser.parse_args()

    # Load settings
    settings = HeartbeatSettings()
    if args.config:
        settings.load_from_file(args.config)
    if args.interval:
        settings.check_interval_seconds = args.interval

    checker = HeartbeatChecker(settings)

    if args.status:
        # Show status and exit
        status = await checker.get_heartbeat_status()
        print(json.dumps(status, indent=2))
        return

    # Start monitoring
    try:
        await checker.start_monitoring()
    except KeyboardInterrupt:
        print("\nReceived interrupt signal, stopping...")
        await checker.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(main())
