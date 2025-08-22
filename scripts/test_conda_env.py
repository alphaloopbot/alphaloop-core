#!/usr/bin/env python3
"""Test script to verify conda environment setup."""

import sys
from importlib import import_module


def test_imports():
    """Test that all required packages can be imported."""
    required_packages = [
        # Core dependencies
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "asyncpg",
        "redis",
        "aio_pika",
        "psutil",
        "aiofiles",
        "yaml",
        "dotenv",
        # Development dependencies
        "pytest",
        "pytest_asyncio",
        "pytest_cov",
        "ruff",
        "mypy",
        "pytest_dotenv",
        "hypothesis",
        "httpx",
        "pre_commit",
    ]

    failed_imports = []

    for package in required_packages:
        try:
            import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)

    if failed_imports:
        print(f"\n❌ Failed to import {len(failed_imports)} packages:")
        for package in failed_imports:
            print(f"  - {package}")
        return False
    else:
        print(f"\n✅ All {len(required_packages)} packages imported successfully!")
        return True


def test_alphaloop_core():
    """Test that alphaloop-core can be imported."""
    try:
        import alphaloop_core  # noqa: F401

        print("✅ alphaloop_core package imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import alphaloop_core: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 Testing AlphaLoop Core conda environment...\n")

    print("📦 Testing package imports:")
    imports_ok = test_imports()

    print("\n🏗️ Testing alphaloop-core package:")
    core_ok = test_alphaloop_core()

    print("\n📊 Test Results:")
    print(f"  Package imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"  Core package: {'✅ PASS' if core_ok else '❌ FAIL'}")

    if imports_ok and core_ok:
        print("\n🎉 All tests passed! Environment is ready.")
        return 0
    else:
        print("\n💥 Some tests failed. Please check your environment setup.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
