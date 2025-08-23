#!/usr/bin/env python3
"""
AlphaLoop System Metrics Service

This service collects system metrics (CPU, RAM, disk) and stores them in the database.
"""

import logging
import os
import time
from datetime import datetime

import psutil
import psycopg2

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class SystemMetricsCollector:
    """Collects system metrics and stores them in the database."""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.metrics_interval = int(os.getenv("METRICS_INTERVAL", 30))
        self.system_database = os.getenv("SYSTEM_DATABASE", "alphaloop_sys")

    def collect_metrics(self):
        """Collect current system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used
            memory_total = memory.total

            # Disk metrics
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent
            disk_used = disk.used
            disk_total = disk.total

            # Network metrics
            network = psutil.net_io_counters()
            bytes_sent = network.bytes_sent
            bytes_recv = network.bytes_recv

            metrics = {
                "timestamp": datetime.now(),
                "cpu_percent": cpu_percent,
                "cpu_count": cpu_count,
                "memory_percent": memory_percent,
                "memory_used": memory_used,
                "memory_total": memory_total,
                "disk_percent": disk_percent,
                "disk_used": disk_used,
                "disk_total": disk_total,
                "bytes_sent": bytes_sent,
                "bytes_recv": bytes_recv,
                "hostname": os.getenv("HOST_HOSTNAME", "unknown"),
            }

            logger.info(
                f"Collected metrics: CPU={cpu_percent}%, Memory={memory_percent}%, Disk={disk_percent}%"
            )
            return metrics

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return None

    def store_metrics(self, metrics):
        """Store metrics in the database."""
        if not metrics or not self.database_url:
            return False

        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()

            # Create table if it doesn't exist
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS system_metrics (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                cpu_percent FLOAT,
                cpu_count INTEGER,
                memory_percent FLOAT,
                memory_used BIGINT,
                memory_total BIGINT,
                disk_percent FLOAT,
                disk_used BIGINT,
                disk_total BIGINT,
                bytes_sent BIGINT,
                bytes_recv BIGINT,
                hostname VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            cursor.execute(create_table_sql)

            # Insert metrics
            insert_sql = """
            INSERT INTO system_metrics (
                timestamp, cpu_percent, cpu_count, memory_percent, memory_used, memory_total,
                disk_percent, disk_used, disk_total, bytes_sent, bytes_recv, hostname
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(
                insert_sql,
                (
                    metrics["timestamp"],
                    metrics["cpu_percent"],
                    metrics["cpu_count"],
                    metrics["memory_percent"],
                    metrics["memory_used"],
                    metrics["memory_total"],
                    metrics["disk_percent"],
                    metrics["disk_used"],
                    metrics["disk_total"],
                    metrics["bytes_sent"],
                    metrics["bytes_recv"],
                    metrics["hostname"],
                ),
            )

            conn.commit()
            cursor.close()
            conn.close()

            logger.info("Metrics stored successfully")
            return True

        except Exception as e:
            logger.error(f"Error storing metrics: {e}")
            return False

    def run(self):
        """Main loop to collect and store metrics."""
        logger.info(f"Starting System Metrics Collector (interval: {self.metrics_interval}s)")

        while True:
            try:
                metrics = self.collect_metrics()
                if metrics:
                    self.store_metrics(metrics)

                time.sleep(self.metrics_interval)

            except KeyboardInterrupt:
                logger.info("Shutting down System Metrics Collector")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(self.metrics_interval)


def main():
    """Main entry point."""
    collector = SystemMetricsCollector()
    collector.run()


if __name__ == "__main__":
    main()
