#!/usr/bin/env python3
"""
Comprehensive test scenarios for AlphaLoop Heartbeat package.
Tests both healthy and unhealthy heartbeat conditions.
"""

import json
from pathlib import Path
import tempfile
import time

import pytest

from infrastructure.alphaloop_heartbeat import (
    HeartbeatChecker,
    HeartbeatGenerator,
    HeartbeatSettings,
)


class TestHeartbeatScenarios:
    """Test various heartbeat scenarios."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def settings(self, temp_dir):
        """Create test settings."""
        settings = HeartbeatSettings()
        settings.heartbeat_directory = temp_dir
        settings.default_interval_seconds = 30
        settings.default_timeout_seconds = 60
        return settings

    @pytest.fixture
    def generator(self, settings):
        """Create heartbeat generator."""
        return HeartbeatGenerator(
            service_name="test-service", settings=settings, interval=30, version="1.0.0"
        )

    @pytest.fixture
    def checker(self, settings):
        """Create heartbeat checker."""
        return HeartbeatChecker(settings)

    def create_heartbeat_file(self, temp_dir: str, service_name: str, timestamp: float, **kwargs):
        """Create a heartbeat file with specific data."""
        heartbeat_data = {
            "service_name": service_name,
            "timestamp": timestamp,
            "status": "healthy",
            "version": "1.0.0",
            "interval_seconds": 30,
            **kwargs,
        }

        file_path = Path(temp_dir) / f"{service_name}.json"
        with open(file_path, "w") as f:
            json.dump(heartbeat_data, f, indent=2)

        return file_path

    async def test_healthy_heartbeat_detection(self, temp_dir, checker):
        """Test that healthy heartbeats are properly detected."""
        print("\n🟢 Testing Healthy Heartbeat Detection")
        print("=" * 50)

        # Create a fresh heartbeat (current time)
        current_time = time.time()
        self.create_heartbeat_file(temp_dir, "healthy-service", current_time)

        print("📄 Created healthy heartbeat for healthy-service")
        print(f"⏰ Timestamp: {current_time}")

        # Check the heartbeat using public API
        health_status = await checker.check_service_health("healthy-service")

        print(f"🔍 Health status: {health_status['healthy']}")
        print(f"📊 Age seconds: {health_status['age_seconds']}")

        # Should be healthy
        assert health_status["healthy"] is True, "Fresh heartbeat should be healthy"
        assert health_status["age_seconds"] < 5, "Age should be very small for fresh heartbeat"

        print("✅ Healthy heartbeat test passed")

    async def test_stale_heartbeat_detection(self, temp_dir, checker):
        """Test that stale heartbeats are properly detected."""
        print("\n🔴 Testing Stale Heartbeat Detection")
        print("=" * 50)

        # Create a stale heartbeat (2 hours ago)
        stale_time = time.time() - (2 * 60 * 60)  # 2 hours ago
        self.create_heartbeat_file(temp_dir, "stale-service", stale_time)

        print("📄 Created stale heartbeat for stale-service")
        print(f"⏰ Timestamp: {stale_time}")
        print("⏰ Age: 2 hours (should be stale)")

        # Check the heartbeat using public API
        health_status = await checker.check_service_health("stale-service")

        print(f"🔍 Health status: {health_status['healthy']}")
        print(f"📊 Age seconds: {health_status['age_seconds']}")
        print(f"❌ Error: {health_status['error']}")

        # Should be unhealthy due to age
        assert health_status["healthy"] is False, "Stale heartbeat should be unhealthy"
        assert health_status["age_seconds"] > 7000, "Age should be over 2 hours"
        assert "too old" in health_status["error"], "Error should mention heartbeat too old"

        print("✅ Stale heartbeat test passed")

    async def test_dead_process_detection(self, temp_dir, checker):
        """Test that dead processes are properly detected."""
        print("\n💀 Testing Dead Process Detection")
        print("=" * 50)

        # Create a heartbeat with a non-existent process ID
        current_time = time.time()
        self.create_heartbeat_file(temp_dir, "dead-process-service", current_time, pid=99999)

        print("📄 Created heartbeat with dead process for dead-process-service")
        print("🆔 Process ID: 99999 (should not exist)")

        # Check the heartbeat using public API
        health_status = await checker.check_service_health("dead-process-service")

        print(f"🔍 Health status: {health_status['healthy']}")
        print(f"❌ Error: {health_status['error']}")

        # Should be unhealthy due to dead process
        assert health_status["healthy"] is False, "Dead process should be unhealthy"
        assert "dead" in health_status["error"], "Error should mention dead process"

        print("✅ Dead process detection test passed")

    async def test_live_process_detection(self, temp_dir, checker):
        """Test that live processes are properly detected."""
        print("\n💚 Testing Live Process Detection")
        print("=" * 50)

        # Get current process ID
        import os

        current_pid = os.getpid()

        # Create a heartbeat with current process ID
        current_time = time.time()
        self.create_heartbeat_file(temp_dir, "live-process-service", current_time, pid=current_pid)

        print("📄 Created heartbeat with live process for live-process-service")
        print(f"🆔 Process ID: {current_pid} (should be running)")

        # Check the heartbeat using public API
        health_status = await checker.check_service_health("live-process-service")

        print(f"🔍 Health status: {health_status['healthy']}")
        print(f"📊 Age seconds: {health_status['age_seconds']}")

        # Should be healthy
        assert health_status["healthy"] is True, "Live process should be healthy"
        assert health_status["age_seconds"] < 5, "Age should be very small for fresh heartbeat"

        print("✅ Live process detection test passed")

    async def test_heartbeat_generation_cycle(self, temp_dir, generator, checker):
        """Test complete heartbeat generation and monitoring cycle."""
        print("\n🔄 Testing Heartbeat Generation Cycle")
        print("=" * 50)

        # Clean the directory first
        for file in Path(temp_dir).glob("*.json"):
            file.unlink()

        # Generate a heartbeat
        await generator.generate_heartbeat()

        # Find the generated file
        heartbeat_files = list(Path(temp_dir).glob("*.json"))
        assert len(heartbeat_files) == 1, "Should generate exactly one heartbeat file"

        heartbeat_file = heartbeat_files[0]
        print(f"📄 Generated heartbeat: {heartbeat_file.name}")

        # Read the generated content
        with open(heartbeat_file) as f:
            data = json.load(f)
            print(f"📝 Service: {data['service_name']}")
            print(f"📝 Timestamp: {data['timestamp']}")
            print(f"📝 Status: {data['status']}")
            print(f"📝 Version: {data['version']}")

        # Check the heartbeat using public API
        health_status = await checker.check_service_health("test-service")

        print(f"🔍 Health status: {health_status['healthy']}")
        print(f"📊 Age seconds: {health_status['age_seconds']}")

        # Should be healthy
        assert health_status["healthy"] is True, "Generated heartbeat should be healthy"
        assert health_status["age_seconds"] < 5, "Age should be very small for fresh heartbeat"

        print("✅ Heartbeat generation cycle test passed")

    async def test_multiple_services_monitoring(self, temp_dir, checker):
        """Test monitoring multiple services simultaneously."""
        print("\n👥 Testing Multiple Services Monitoring")
        print("=" * 50)

        # Clean the directory first
        for file in Path(temp_dir).glob("*.json"):
            file.unlink()

        # Create multiple heartbeat files with different states
        current_time = time.time()
        stale_time = time.time() - (3 * 60 * 60)  # 3 hours ago

        # Healthy service
        self.create_heartbeat_file(temp_dir, "service-1", current_time)

        # Stale service (3 hours old)
        self.create_heartbeat_file(temp_dir, "service-2", stale_time)

        # Service with dead process
        self.create_heartbeat_file(temp_dir, "service-3", current_time, pid=99999)

        print("📄 Created 3 services:")
        print("  🟢 service-1: Healthy")
        print("  🔴 service-2: Stale (3 hours old)")
        print("  💀 service-3: Dead process")

        # Check all services using public API
        all_services_status = await checker.check_all_services(
            ["service-1", "service-2", "service-3"]
        )

        print(f"🔍 All healthy: {all_services_status['all_healthy']}")
        print(f"📊 Healthy count: {all_services_status['healthy_count']}")
        print(f"📊 Total count: {all_services_status['total_count']}")

        # Should have 1 healthy, 2 unhealthy
        assert all_services_status["all_healthy"] is False, "Not all services should be healthy"
        assert all_services_status["healthy_count"] == 1, "Should have exactly 1 healthy service"
        assert all_services_status["total_count"] == 3, "Should have exactly 3 total services"

        # Check individual services
        service_1_status = all_services_status["services"]["service-1"]
        service_2_status = all_services_status["services"]["service-2"]
        service_3_status = all_services_status["services"]["service-3"]

        assert service_1_status["healthy"] is True, "Service 1 should be healthy"
        assert service_2_status["healthy"] is False, "Service 2 should be stale"
        assert service_3_status["healthy"] is False, "Service 3 should have dead process"

        print("✅ Multiple services monitoring test passed")

    async def test_heartbeat_file_corruption(self, temp_dir, checker):
        """Test handling of corrupted heartbeat files."""
        print("\n💥 Testing Corrupted Heartbeat File Handling")
        print("=" * 50)

        # Create a corrupted JSON file
        corrupted_file = Path(temp_dir) / "corrupted-service.json"
        with open(corrupted_file, "w") as f:
            f.write('{"invalid": json content}')

        print(f"📄 Created corrupted heartbeat: {corrupted_file.name}")

        # Check the heartbeat using public API
        health_status = await checker.check_service_health("corrupted-service")

        print(f"🔍 Health status: {health_status['healthy']}")
        print(f"❌ Error: {health_status['error']}")

        # Should be unhealthy due to corruption
        assert health_status["healthy"] is False, "Corrupted file should be unhealthy"
        assert "Invalid JSON" in health_status["error"], "Error should mention invalid JSON"

        print("✅ Corrupted heartbeat file test passed")

    async def test_missing_timestamp_handling(self, temp_dir, checker):
        """Test handling of heartbeat files without timestamps."""
        print("\n❓ Testing Missing Timestamp Handling")
        print("=" * 50)

        # Create a heartbeat file without timestamp
        heartbeat_data = {
            "service_name": "no-timestamp-service",
            "status": "healthy",
            "version": "1.0.0",
        }

        no_timestamp_file = Path(temp_dir) / "no-timestamp-service.json"
        with open(no_timestamp_file, "w") as f:
            json.dump(heartbeat_data, f)

        print(f"📄 Created heartbeat without timestamp: {no_timestamp_file.name}")

        # Check the heartbeat using public API
        health_status = await checker.check_service_health("no-timestamp-service")

        print(f"🔍 Health status: {health_status['healthy']}")
        print(f"❌ Error: {health_status['error']}")

        # Should be unhealthy due to missing timestamp
        assert health_status["healthy"] is False, "Missing timestamp should be unhealthy"
        assert "No timestamp" in health_status["error"], "Error should mention missing timestamp"

        print("✅ Missing timestamp handling test passed")


if __name__ == "__main__":
    # Run pytest instead of main function
    import subprocess
    import sys

    subprocess.run([sys.executable, "-m", "pytest", __file__, "-v"])
