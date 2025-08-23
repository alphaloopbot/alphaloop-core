"""File utilities for heartbeat management."""

import os
from pathlib import Path


def get_heartbeat_directory() -> Path:
    """Get the heartbeat directory path."""
    # Try environment variable first
    env_dir = os.getenv("HEARTBEAT_DIRECTORY")
    if env_dir:
        return Path(env_dir)

    # Default to /tmp/heartbeats
    default_dir = Path("/tmp/heartbeats")
    default_dir.mkdir(parents=True, exist_ok=True)
    return default_dir


def ensure_directory_exists(directory: Path) -> None:
    """Ensure a directory exists, creating it if necessary."""
    directory.mkdir(parents=True, exist_ok=True)


def get_heartbeat_file_path(service_name: str, directory: Path | None = None) -> Path:
    """Get the heartbeat file path for a service."""
    if directory is None:
        directory = get_heartbeat_directory()

    return directory / f"{service_name}.json"


def cleanup_old_heartbeats(directory: Path, max_age_hours: int = 24) -> int:
    """Clean up old heartbeat files."""
    import time

    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    cleaned_count = 0

    for heartbeat_file in directory.glob("*.json"):
        try:
            file_age = current_time - heartbeat_file.stat().st_mtime
            if file_age > max_age_seconds:
                heartbeat_file.unlink()
                cleaned_count += 1
        except Exception:
            # Skip files that can't be processed
            continue

    return cleaned_count
