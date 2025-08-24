"""
System Metrics Service

This service collects system metrics (CPU, RAM, disk) and stores them in the database.
Uses alphaloop infrastructure packages for logging, storage, and heartbeat monitoring.
"""

import asyncio
import os
import time
from datetime import datetime
from typing import Any

import psutil
from alphaloop_heartbeat import HeartbeatGenerator
from alphaloop_logging import AlphaLoopLogger, LoggingConfig
from alphaloop_storage import TableHandler, create_database_manager


class SystemMetricsService:
    """System metrics collection service using alphaloop infrastructure."""

    def __init__(self):
        """Initialize the system metrics service with infrastructure components."""
        # Initialize infrastructure components
        logging_config = LoggingConfig.from_env(app_name="system-metrics-service")
        self.logger = AlphaLoopLogger(logging_config)

        # Create database manager from environment variables
        self.db_manager = create_database_manager(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "alphaloop_sys"),
            username=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            port=int(os.getenv("DB_PORT", "5432")),
        )

        # Initialize table handlers for both metadata and metrics
        self.metadata_handler = TableHandler("system_attributes", self.db_manager)
        self.metrics_handler = TableHandler("system_metrics", self.db_manager)
        self.heartbeat_generator = HeartbeatGenerator("system-metrics")

        # Configuration
        self.metrics_interval = int(os.getenv("METRICS_INTERVAL", 30))
        self.system_database = os.getenv("SYSTEM_DATABASE", "alphaloop_sys")

        # Get or create system metadata (will be initialized in first async call)
        self.metadata_id = None

        self.logger.info_sync(
            f"System Metrics Service initialized (interval: {self.metrics_interval}s)"
        )

    async def _get_or_create_metadata(self) -> int:
        """Get existing metadata or create new one for this host."""
        try:
            hostname = os.getenv("HOST_HOSTNAME", "unknown")

            # Try to find existing metadata for this host
            # For now, we'll create new metadata each time (in production, you'd query existing)
            metadata = {
                "host_name": hostname,
                "system_name": (
                    os.uname().sysname if hasattr(os, "uname") else "Unknown"
                ),
                "node_name": os.uname().nodename if hasattr(os, "uname") else hostname,
                "machine": os.uname().machine if hasattr(os, "uname") else "Unknown",
                "kernel_version": (
                    os.uname().release if hasattr(os, "uname") else "Unknown"
                ),
                "cpu_cores": psutil.cpu_count(logical=False),
                "cpu_cores_logical": psutil.cpu_count(logical=True),
                "ram_total": float(psutil.virtual_memory().total),  # Match YAML schema
                "ssd_total": float(psutil.disk_usage("/").total),  # Match YAML schema
                "boot_time": datetime.fromtimestamp(psutil.boot_time()),
                "app_start_time": datetime.now(),
            }

            # Insert metadata and return the ID
            metadata_id = await self.metadata_handler.insert_data(metadata)
            return metadata_id

        except Exception as e:
            self.logger.error_sync(f"Error creating metadata: {e}")
            # Return a default metadata ID (1) for now
            return 1

    def collect_metrics(self) -> dict[str, Any] | None:
        """Collect current system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk metrics
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent

            # Network metrics (placeholder for future use)
            # network = psutil.net_io_counters()

            # Get real IP address
            import json
            import urllib.request

            def get_public_ip():
                """Get the actual public IP address."""
                try:
                    # Method 1: Use a public IP service
                    with urllib.request.urlopen(
                        "https://api.ipify.org?format=json", timeout=5
                    ) as response:
                        data = json.loads(response.read().decode())
                        return data["ip"]
                except Exception:
                    try:
                        # Method 2: Alternative service
                        with urllib.request.urlopen(
                            "https://httpbin.org/ip", timeout=5
                        ) as response:
                            data = json.loads(response.read().decode())
                            return data["origin"]
                    except Exception:
                        # If we can't get public IP, return None instead of local IP
                        return None

            ip_address = get_public_ip()

            # Try to get CPU temperature (works on Raspberry Pi)
            cpu_temperature = None
            try:
                temp_path = "/sys/class/thermal/thermal_zone0/temp"
                if os.path.exists(temp_path):
                    with open(temp_path) as f:
                        cpu_temperature = int(f.read().strip()) / 1000.0
            except Exception:
                pass  # Temperature not available

            # Try to get CPU frequency (works on Raspberry Pi)
            cpu_speed = None
            try:
                freq_path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
                if os.path.exists(freq_path):
                    with open(freq_path) as f:
                        cpu_speed = int(f.read().strip()) / 1000.0
            except Exception:
                pass  # Frequency not available

            # Build metrics with real data
            metrics = {
                "metadata_id": self.metadata_id,
                "timestamp_id": int(time.time()),
                "cpu_usage": cpu_percent,
                "ram_usage": memory_percent,
                "ssd_usage": disk_percent,
            }

            # Only add IP address if we actually have one
            if ip_address is not None:
                metrics["ip_address"] = ip_address

            # Add optional fields only if we have real data
            if cpu_temperature is not None:
                metrics["cpu_temperature"] = cpu_temperature

            if cpu_speed is not None:
                metrics["cpu_speed"] = int(cpu_speed)

            if cpu_freq and cpu_freq.current:
                metrics["cpu_speed"] = int(cpu_freq.current / 1000)  # Convert to MHz

            # Add per-core usage if available
            if cpu_per_core:
                cores_usage = {
                    f"core_{i}": usage for i, usage in enumerate(cpu_per_core)
                }
                metrics["cores_usage"] = cores_usage
                metrics["core_usage_max"] = max(cpu_per_core)
                metrics["core_usage_min"] = min(cpu_per_core)

            # Use logger's built-in sync method
            self.logger.info_sync(
                f"Collected metrics: CPU={cpu_percent}%, Memory={memory_percent}%, Disk={disk_percent}%"
            )

            return metrics

        except Exception as e:
            # Use logger's built-in sync method for errors
            self.logger.error_sync(f"Error collecting metrics: {e}")
            return None

    async def store_metrics_async(self, metrics: dict[str, Any]) -> bool:
        """Store metrics in the database using alphaloop-storage (async)."""
        if not metrics:
            return False

        try:
            # Initialize metadata_id if not set
            if self.metadata_id is None:
                self.metadata_id = await self._get_or_create_metadata()
                # Update metrics with the metadata_id
                metrics["metadata_id"] = self.metadata_id

            # Use the metrics handler to store metrics
            success = await self.metrics_handler.insert_data(metrics)

            if success:
                await self.logger.info(f"Stored metrics: {len(metrics)} fields")
                return True
            else:
                await self.logger.error("Failed to store metrics using infrastructure")
                return False

        except Exception as e:
            await self.logger.error(f"Error storing metrics: {e}")
            return False

    def store_metrics(self, metrics: dict[str, Any]) -> bool:
        """Store metrics in the database (synchronous wrapper)."""
        if not metrics:
            return False

        try:
            # Run async operation in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self.store_metrics_async(metrics))
                return result
            finally:
                loop.close()
        except Exception as e:
            self.logger.error_sync(f"Error in store_metrics: {e}")
            return False

    def collect_and_store_metrics(self) -> bool:
        """Collect and store metrics in one operation."""
        try:
            # Generate heartbeat
            self.heartbeat_generator.generate_heartbeat()

            # Collect metrics
            metrics = self.collect_metrics()
            if metrics:
                return self.store_metrics(metrics)
            return False

        except Exception as e:
            self.logger.error_sync(f"Error in collect_and_store_metrics: {e}")
            return False

    def run_forever(self) -> None:
        """Main loop to collect and store metrics continuously."""
        self.logger.info(
            f"Starting System Metrics Service (interval: {self.metrics_interval}s)"
        )

        while True:
            try:
                self.collect_and_store_metrics()
                time.sleep(self.metrics_interval)

            except KeyboardInterrupt:
                self.logger.info("Shutting down System Metrics Service")
                break
            except Exception as e:
                self.logger.error_sync(f"Error in main loop: {e}")
                time.sleep(self.metrics_interval)

    def run_once(self) -> bool:
        """Run one collection cycle and return success status."""
        return self.collect_and_store_metrics()


if __name__ == "__main__":
    """Main entry point for the System Metrics Service."""
    service = SystemMetricsService()
    service.run_forever()
