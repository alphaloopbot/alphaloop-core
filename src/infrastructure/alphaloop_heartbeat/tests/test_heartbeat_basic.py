#!/usr/bin/env python3
"""
Basic test script for AlphaLoop Heartbeat package.
"""

import asyncio
import tempfile
from pathlib import Path

from alphaloop_heartbeat import HeartbeatChecker, HeartbeatGenerator, HeartbeatSettings


async def test_heartbeat_generation():
    """Test basic heartbeat generation."""
    print("🫀 Testing Heartbeat Generation")
    print("=" * 40)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create settings
        settings = HeartbeatSettings()
        settings.heartbeat_directory = temp_dir
        settings.default_interval_seconds = 5

        # Create generator
        generator = HeartbeatGenerator(
            service_name="test-service", settings=settings, interval=5, version="1.0.0"
        )

        print(f"📁 Heartbeat directory: {temp_dir}")
        print(f"🔧 Service name: {generator.service_name}")
        print(f"⏱️  Interval: {generator._interval}s")
        print(f"📦 Version: {generator.version}")

        # Generate a single heartbeat
        await generator.generate_heartbeat()

        # Check if file was created
        heartbeat_files = list(Path(temp_dir).glob("*.json"))
        print(f"📄 Created {len(heartbeat_files)} heartbeat file(s)")

        if heartbeat_files:
            print(f"📄 File: {heartbeat_files[0].name}")
            # Read and display content
            with open(heartbeat_files[0]) as f:
                content = f.read()
                print(f"📝 Content: {content[:100]}...")

        print("✅ Heartbeat generation test completed\n")


async def test_heartbeat_checking():
    """Test basic heartbeat checking."""
    print("🔍 Testing Heartbeat Checking")
    print("=" * 40)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create settings
        settings = HeartbeatSettings()
        settings.heartbeat_directory = temp_dir
        settings.default_timeout_seconds = 30

        # Create checker
        checker = HeartbeatChecker(settings)

        print(f"📁 Monitoring directory: {settings.heartbeat_directory}")
        print(f"⏱️  Default timeout: {settings.default_timeout_seconds}s")

        # Create a test heartbeat file
        test_file = Path(temp_dir) / "test-service.json"
        test_content = """{
  "service_name": "test-service",
  "timestamp": 1755981887.0,
  "status": "healthy",
  "version": "1.0.0",
  "interval_seconds": 30
}"""

        with open(test_file, "w") as f:
            f.write(test_content)

        print(f"📄 Created test heartbeat file: {test_file.name}")

        # Check the heartbeat using the public API
        health_status = await checker.check_service_health("test-service")

        print(f"🔍 Health status: {health_status['healthy']}")
        print(f"📊 Age seconds: {health_status['age_seconds']}")
        if health_status["error"]:
            print(f"❌ Error: {health_status['error']}")

        print("✅ Heartbeat checking test completed\n")


async def main():
    """Run all tests."""
    print("🚀 AlphaLoop Heartbeat Package Test")
    print("=" * 50)
    print()

    try:
        await test_heartbeat_generation()
        await test_heartbeat_checking()

        print("🎉 All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
