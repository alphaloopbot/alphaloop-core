"""Pytest configuration for AlphaLoop Core tests."""

import os
from pathlib import Path
import sys

# Add the src directory to Python path for imports
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Set up environment variables for testing
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_LEVEL", "DEBUG")
os.environ.setdefault("API_KEY", "test-key")


def pytest_ignore_collect(collection_path: Path, config):
    """Ignore infrastructure test directories."""
    # Ignore any test dirs living under src/infrastructure/**/tests
    parts = collection_path.parts
    return "src" in parts and "infrastructure" in parts and "tests" in parts
