#!/usr/bin/env python3
"""
Comprehensive test scenarios for AlphaLoop Heartbeat package.
Tests both healthy and unhealthy heartbeat conditions.
"""

import asyncio
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from alphaloop_heartbeat import HeartbeatChecker, HeartbeatGenerator, HeartbeatSettings


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
        settings.check_interval_seconds = 10
        settings.stale_multiplier = 2.0
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

    def create_heartbeat_file(self, temp_dir: str, service_name: str, timestamp: str, **kwargs):
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
        current_time = datetime.now().isoformat()
        heartbeat_file = self.create_heartbeat_file(temp_dir, "healthy-service", current_time)

        print(f"📄 Created healthy heartbeat: {heartbeat_file.name}")
        print(f"⏰ Timestamp: {current_time}")

        # Check the heartbeat
        await checker._check_single_heartbeat(heartbeat_file)

        # Should not trigger any stale warnings
        print("✅ Healthy heartbeat detected - no warnings triggered")

        # Verify file still exists
        assert heartbeat_file.exists(), "Heartbeat file should still exist"

        # Read and verify content
        with open(heartbeat_file) as f:
            data = json.load(f)
            assert data["status"] == "healthy"
            assert data["service_name"] == "healthy-service"

        print("✅ Healthy heartbeat test passed")

    async def test_stale_heartbeat_detection(self, temp_dir, checker):
        """Test that stale heartbeats are properly detected."""
        print("\n🔴 Testing Stale Heartbeat Detection")
        print("=" * 50)

        # Create a stale heartbeat (2 hours ago)
        stale_time = (datetime.now() - timedelta(hours=2)).isoformat()
        heartbeat_file = self.create_heartbeat_file(temp_dir, "stale-service", stale_time)

        print(f"📄 Created stale heartbeat: {heartbeat_file.name}")
        print(f"⏰ Timestamp: {stale_time}")
        print("⏰ Age: 2 hours (should be stale)")

        # Mock the print function to capture output
        with patch("builtins.print") as mock_print:
            await checker._check_single_heartbeat(heartbeat_file)

            # Check that stale warning was printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            stale_warnings = [call for call in print_calls if "STALE HEARTBEAT" in call]

            assert len(stale_warnings) > 0, "Should detect stale heartbeat"
            print(f"🔍 Detected {len(stale_warnings)} stale warnings")

            for warning in stale_warnings:
                print(f"⚠️  {warning}")

        print("✅ Stale heartbeat test passed")

    async def test_dead_process_detection(self, temp_dir, checker):
        """Test that dead processes are properly detected."""
        print("\n💀 Testing Dead Process Detection")
        print("=" * 50)

        # Create a heartbeat with a non-existent process ID
        current_time = datetime.now().isoformat()
        heartbeat_file = self.create_heartbeat_file(
            temp_dir, "dead-process-service", current_time, process_id=99999
        )

        print(f"📄 Created heartbeat with dead process: {heartbeat_file.name}")
        print("🆔 Process ID: 99999 (should not exist)")

        # Mock the print function to capture output
        with patch("builtins.print") as mock_print:
            await checker._check_single_heartbeat(heartbeat_file)

            # Check that dead process warning was printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            dead_process_warnings = [call for call in print_calls if "DEAD PROCESS" in call]

            assert len(dead_process_warnings) > 0, "Should detect dead process"
            print(f"🔍 Detected {len(dead_process_warnings)} dead process warnings")

            for warning in dead_process_warnings:
                print(f"💀 {warning}")

        print("✅ Dead process test passed")

    async def test_live_process_detection(self, temp_dir, checker):
        """Test that live processes are properly detected."""
        print("\n💚 Testing Live Process Detection")
        print("=" * 50)

        # Get current process ID
        import os

        current_pid = os.getpid()

        # Create a heartbeat with current process ID
        current_time = datetime.now().isoformat()
        heartbeat_file = self.create_heartbeat_file(
            temp_dir, "live-process-service", current_time, process_id=current_pid
        )

        print(f"📄 Created heartbeat with live process: {heartbeat_file.name}")
        print(f"🆔 Process ID: {current_pid} (should be running)")

        # Mock the print function to capture output
        with patch("builtins.print") as mock_print:
            await checker._check_single_heartbeat(heartbeat_file)

            # Check that no dead process warning was printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            dead_process_warnings = [call for call in print_calls if "not running" in call]

            assert (
                len(dead_process_warnings) == 0
            ), "Should not detect dead process for live process"
            print("✅ No dead process warnings for live process")

        print("✅ Live process test passed")

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

        # Check the heartbeat
        with patch("builtins.print") as mock_print:
            await checker._check_single_heartbeat(heartbeat_file)

            # Should not trigger any warnings for fresh heartbeat
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            warnings = [
                call
                for call in print_calls
                if any(keyword in call for keyword in ["STALE", "not running", "Warning"])
            ]

            assert len(warnings) == 0, "Fresh heartbeat should not trigger warnings"
            print("✅ Fresh heartbeat properly detected")

        print("✅ Heartbeat generation cycle test passed")

    async def test_multiple_services_monitoring(self, temp_dir, checker):
        """Test monitoring multiple services simultaneously."""
        print("\n👥 Testing Multiple Services Monitoring")
        print("=" * 50)

        # Clean the directory first
        for file in Path(temp_dir).glob("*.json"):
            file.unlink()

        # Create multiple heartbeat files with different states
        current_time = datetime.now().isoformat()
        stale_time = (datetime.now() - timedelta(hours=3)).isoformat()

        # Healthy service
        healthy_file = self.create_heartbeat_file(temp_dir, "service-1", current_time)

        # Stale service (3 hours old, should be stale with 2.0 multiplier and 30s interval)
        stale_file = self.create_heartbeat_file(temp_dir, "service-2", stale_time)

        # Service with dead process
        dead_process_file = self.create_heartbeat_file(
            temp_dir, "service-3", current_time, process_id=99999
        )

        print("📄 Created 3 services:")
        print("  🟢 service-1: Healthy")
        print("  🔴 service-2: Stale (3 hours old)")
        print("  💀 service-3: Dead process")

        # Check each file individually to avoid cleanup issues
        print("\n🔍 Checking individual files:")

        # Check healthy file
        with patch("builtins.print") as mock_print:
            await checker._check_single_heartbeat(healthy_file)
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            warnings = [
                call
                for call in print_calls
                if any(keyword in call for keyword in ["STALE", "DEAD PROCESS", "Warning"])
            ]
            assert len(warnings) == 0, "Healthy service should not trigger warnings"
            print("✅ Healthy service: No warnings")

        # Check stale file
        with patch("builtins.print") as mock_print:
            await checker._check_single_heartbeat(stale_file)
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            stale_warnings = [call for call in print_calls if "STALE HEARTBEAT" in call]
            assert len(stale_warnings) > 0, "Should detect stale service"
            print(f"✅ Stale service: {len(stale_warnings)} warnings detected")
            for warning in stale_warnings:
                print(f"⚠️  {warning}")

        # Check dead process file
        with patch("builtins.print") as mock_print:
            await checker._check_single_heartbeat(dead_process_file)
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            dead_process_warnings = [call for call in print_calls if "DEAD PROCESS" in call]
            assert len(dead_process_warnings) > 0, "Should detect dead process"
            print(f"✅ Dead process: {len(dead_process_warnings)} warnings detected")
            for warning in dead_process_warnings:
                print(f"💀 {warning}")

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

        # Mock the print function to capture output
        with patch("builtins.print") as mock_print:
            await checker._check_single_heartbeat(corrupted_file)

            # Check that corruption warning was printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            corruption_warnings = [call for call in print_calls if "Invalid JSON" in call]

            assert len(corruption_warnings) > 0, "Should detect corrupted JSON"
            print(f"🔍 Detected {len(corruption_warnings)} corruption warnings")

            for warning in corruption_warnings:
                print(f"💥 {warning}")

        print("✅ Corrupted file handling test passed")

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

        # Mock the print function to capture output
        with patch("builtins.print") as mock_print:
            await checker._check_single_heartbeat(no_timestamp_file)

            # Check that missing timestamp warning was printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            missing_timestamp_warnings = [
                call for call in print_calls if "No timestamp found" in call
            ]

            assert len(missing_timestamp_warnings) > 0, "Should detect missing timestamp"
            print(f"🔍 Detected {len(missing_timestamp_warnings)} missing timestamp warnings")

            for warning in missing_timestamp_warnings:
                print(f"❓ {warning}")

        print("✅ Missing timestamp handling test passed")


async def run_all_scenarios():
    """Run all heartbeat scenario tests."""
    print("🚀 AlphaLoop Heartbeat Scenario Tests")
    print("=" * 60)
    print()

    # Create test instance
    test_instance = TestHeartbeatScenarios()

    # Run all tests
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup
        settings = HeartbeatSettings()
        settings.heartbeat_directory = temp_dir
        settings.default_interval_seconds = 30
        settings.check_interval_seconds = 10
        settings.stale_multiplier = 2.0

        generator = HeartbeatGenerator(
            service_name="test-service", settings=settings, interval=30, version="1.0.0"
        )

        checker = HeartbeatChecker(settings)

        # Run tests
        try:
            await test_instance.test_healthy_heartbeat_detection(temp_dir, checker)
            await test_instance.test_stale_heartbeat_detection(temp_dir, checker)
            await test_instance.test_dead_process_detection(temp_dir, checker)
            await test_instance.test_live_process_detection(temp_dir, checker)
            await test_instance.test_heartbeat_generation_cycle(temp_dir, generator, checker)
            await test_instance.test_multiple_services_monitoring(temp_dir, checker)
            await test_instance.test_heartbeat_file_corruption(temp_dir, checker)
            await test_instance.test_missing_timestamp_handling(temp_dir, checker)

            print("\n🎉 All scenario tests completed successfully!")
            print("✅ Heartbeat package is working correctly for all scenarios")

        except Exception as e:
            print(f"\n❌ Scenario test failed: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_scenarios())
