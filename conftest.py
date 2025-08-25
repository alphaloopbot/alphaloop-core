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


def pytest_ignore_collect(collection_path):
    """Ignore infrastructure test directories."""
    p = str(collection_path)
    # ignore any test dirs living under src/infrastructure/**/tests
    return "src/infrastructure" in p and "/tests" in p
