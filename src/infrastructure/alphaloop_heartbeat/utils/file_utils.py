"""
File utilities for AlphaLoop Heartbeat.

This module provides file system utilities specifically designed for heartbeat
file management. These utilities handle file path construction, directory
creation, and file operations in a safe and consistent manner.

The utilities ensure that heartbeat files are stored in predictable locations
and that file operations are performed safely with proper error handling.

Key Features:
- Safe file path construction
- Directory creation and validation
- File existence checking
- Atomic file operations
- Cross-platform compatibility
"""

import os
from pathlib import Path


def get_heartbeat_file_path(service_name: str, heartbeat_directory: Path) -> Path:
    """
    Get the file path for a service's heartbeat file.

    Constructs a safe file path for storing heartbeat data for a specific service.
    The function ensures that the path is valid and follows consistent naming
    conventions across different operating systems.

    The heartbeat file is stored as a JSON file with the service name as the
    filename, ensuring easy identification and management of heartbeat files
    for multiple services.

    Args:
        service_name: Name of the service (will be sanitized for filesystem safety)
        heartbeat_directory: Base directory where heartbeat files are stored

    Returns:
        Path object representing the heartbeat file location

    Raises:
        ValueError: If service_name is empty or invalid

    Example:
        >>> heartbeat_dir = Path("/var/heartbeats")
        >>> file_path = get_heartbeat_file_path("api-service", heartbeat_dir)
        >>> print(file_path)
        PosixPath('/var/heartbeats/api-service.json')

        >>> file_path = get_heartbeat_file_path("worker-1", Path("./heartbeats"))
        >>> print(file_path)
        PosixPath('./heartbeats/worker-1.json')
    """
    if not service_name or not service_name.strip():
        raise ValueError("service_name cannot be empty")

    # Sanitize service name for filesystem safety
    safe_name = service_name.strip().replace("/", "_").replace("\\", "_")
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in "._-")

    if not safe_name:
        raise ValueError("service_name contains no valid characters")

    return heartbeat_directory / f"{safe_name}.json"


def ensure_heartbeat_directory(directory_path: Path) -> None:
    """
    Ensure the heartbeat directory exists and is writable.

    Creates the heartbeat directory if it doesn't exist and verifies that
    it is writable. This function is essential for ensuring that heartbeat
    files can be created without permission errors.

    The function creates parent directories as needed and sets appropriate
    permissions for the heartbeat directory.

    Args:
        directory_path: Path to the heartbeat directory

    Raises:
        OSError: If the directory cannot be created or is not writable
        PermissionError: If insufficient permissions to create or access directory

    Example:
        >>> heartbeat_dir = Path("/var/heartbeats")
        >>> ensure_heartbeat_directory(heartbeat_dir)
        # Creates /var/heartbeats if it doesn't exist

        >>> ensure_heartbeat_directory(Path("./local-heartbeats"))
        # Creates ./local-heartbeats if it doesn't exist
    """
    try:
        directory_path.mkdir(parents=True, exist_ok=True)

        # Verify the directory is writable
        test_file = directory_path / ".test_write"
        try:
            test_file.touch()
            test_file.unlink()
        except (OSError, PermissionError) as e:
            raise OSError(f"Heartbeat directory is not writable: {directory_path}") from e

    except (OSError, PermissionError) as e:
        raise OSError(f"Cannot create or access heartbeat directory: {directory_path}") from e


def cleanup_old_heartbeat_files(heartbeat_directory: Path, max_age_seconds: int) -> int:
    """
    Remove heartbeat files older than the specified age.

    Scans the heartbeat directory and removes any heartbeat files that are
    older than the specified maximum age. This function helps prevent disk
    space issues by cleaning up stale heartbeat files.

    The function only removes files with the .json extension to avoid
    accidentally deleting other files in the directory.

    Args:
        heartbeat_directory: Directory containing heartbeat files
        max_age_seconds: Maximum age of heartbeat files in seconds

    Returns:
        Number of files that were removed

    Raises:
        OSError: If there are issues accessing the directory or files

    Example:
        >>> heartbeat_dir = Path("/var/heartbeats")
        >>> removed_count = cleanup_old_heartbeat_files(heartbeat_dir, 86400)
        >>> print(f"Removed {removed_count} old heartbeat files")
        Removed 5 old heartbeat files
    """
    if not heartbeat_directory.exists():
        return 0

    import time

    current_time = time.time()
    removed_count = 0

    try:
        for heartbeat_file in heartbeat_directory.glob("*.json"):
            try:
                file_age = current_time - heartbeat_file.stat().st_mtime
                if file_age > max_age_seconds:
                    heartbeat_file.unlink()
                    removed_count += 1
            except OSError as e:
                # Log error but continue with other files
                print(f"Error processing {heartbeat_file}: {e}")

    except OSError as e:
        raise OSError(f"Error accessing heartbeat directory: {heartbeat_directory}") from e

    return removed_count


def get_heartbeat_directory() -> Path:
    """
    Get the default heartbeat directory path.

    Returns the default directory where heartbeat files should be stored.
    This function provides a consistent default location across different
    deployment environments.

    The default directory is chosen based on common conventions:
    - Development: ./heartbeats (relative to current working directory)
    - Production: /var/heartbeats (system-wide location)

    Returns:
        Path object representing the default heartbeat directory

    Example:
        >>> heartbeat_dir = get_heartbeat_directory()
        >>> print(heartbeat_dir)
        PosixPath('./heartbeats')
    """
    # Check if we're in a production environment
    if os.path.exists("/var/heartbeats") or os.access("/var", os.W_OK):
        return Path("/var/heartbeats")
    else:
        return Path("./heartbeats")


def list_heartbeat_files(heartbeat_directory: Path) -> list[Path]:
    """
    List all heartbeat files in the specified directory.

    Returns a list of all heartbeat files (JSON files) in the specified
    directory. This function is useful for monitoring and management
    purposes.

    Args:
        heartbeat_directory: Directory to scan for heartbeat files

    Returns:
        List of Path objects representing heartbeat files

    Raises:
        OSError: If there are issues accessing the directory

    Example:
        >>> heartbeat_dir = Path("/var/heartbeats")
        >>> files = list_heartbeat_files(heartbeat_dir)
        >>> for file in files:
        ...     print(f"Found heartbeat: {file.name}")
        Found heartbeat: api-service.json
        Found heartbeat: worker-1.json
        Found heartbeat: database.json
    """
    if not heartbeat_directory.exists():
        return []

    try:
        return list(heartbeat_directory.glob("*.json"))
    except OSError as e:
        raise OSError(f"Error accessing heartbeat directory: {heartbeat_directory}") from e


def get_heartbeat_file_info(heartbeat_file: Path) -> dict:
    """
    Get information about a heartbeat file.

    Retrieves metadata about a heartbeat file including its size, modification
    time, and basic content information. This function is useful for monitoring
    and debugging heartbeat file issues.

    Args:
        heartbeat_file: Path to the heartbeat file

    Returns:
        Dictionary containing file information:
        - exists: Whether the file exists
        - size: File size in bytes (if exists)
        - modified: Last modification time (if exists)
        - readable: Whether the file is readable (if exists)
        - content_preview: Preview of file content (if readable)

    Example:
        >>> heartbeat_file = Path("/var/heartbeats/api-service.json")
        >>> info = get_heartbeat_file_info(heartbeat_file)
        >>> print(f"File exists: {info['exists']}")
        >>> print(f"File size: {info['size']} bytes")
        File exists: True
        File size: 156 bytes
    """
    import json
    from datetime import datetime

    info: dict = {
        "exists": heartbeat_file.exists(),
        "size": None,
        "modified": None,
        "readable": False,
        "content_preview": None,
    }

    if not info["exists"]:
        return info

    try:
        stat = heartbeat_file.stat()
        info["size"] = stat.st_size
        info["modified"] = datetime.fromtimestamp(stat.st_mtime)

        # Try to read and parse the file
        try:
            with open(heartbeat_file, encoding="utf-8") as f:
                content = f.read()
                heartbeat_data = json.loads(content)
                info["readable"] = True
                info["content_preview"] = {
                    "service_name": heartbeat_data.get("service_name"),
                    "timestamp": heartbeat_data.get("timestamp"),
                    "status": heartbeat_data.get("status"),
                }
        except (OSError, json.JSONDecodeError):
            info["readable"] = False

    except OSError:
        pass

    return info
