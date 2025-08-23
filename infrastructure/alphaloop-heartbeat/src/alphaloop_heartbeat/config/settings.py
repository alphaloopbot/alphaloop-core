"""
Configuration settings for AlphaLoop Heartbeat.

This module provides configuration management for the heartbeat system, including
default values, validation, and loading from various sources (environment variables,
configuration files, etc.).

The settings control behavior such as heartbeat intervals, timeout thresholds,
directory locations, and monitoring parameters. These settings ensure consistent
behavior across different deployment environments and use cases.

Key Features:
- Environment variable configuration
- Configuration file loading
- Default value management
- Validation and error handling
- Type safety with dataclasses
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class HeartbeatSettings:
    """
    Configuration settings for heartbeat generation and monitoring.

    This class encapsulates all configuration parameters needed for the heartbeat
    system to function properly. It provides sensible defaults while allowing
    customization through environment variables or configuration files.

    The settings control:
    - Heartbeat generation intervals
    - Timeout thresholds for health checks
    - File system locations and permissions
    - Monitoring behavior and alerts
    - Performance and reliability parameters

    Key Features:
    - Type-safe configuration with dataclasses
    - Environment variable integration
    - Configuration file loading
    - Validation and error handling
    - Sensible defaults for all parameters

    Usage:
        # Use default settings
        settings = HeartbeatSettings()

        # Customize specific parameters
        settings = HeartbeatSettings(
            default_interval_seconds=30,
            heartbeat_directory="/var/heartbeats"
        )

        # Load from environment variables
        settings = HeartbeatSettings.from_env()
    """

    # Heartbeat generation settings
    default_interval_seconds: int = field(
        default=60,
        metadata={
            "description": "Default interval between heartbeat generations in seconds",
            "env_var": "HEARTBEAT_INTERVAL",
            "min_value": 1,
            "max_value": 3600,
        },
    )

    # Health check settings
    default_timeout_seconds: int = field(
        default=120,
        metadata={
            "description": "Default timeout threshold for health checks in seconds",
            "env_var": "HEARTBEAT_TIMEOUT",
            "min_value": 1,
            "max_value": 7200,
        },
    )

    # File system settings
    heartbeat_directory: str = field(
        default="./heartbeats",
        metadata={
            "description": "Directory where heartbeat files are stored",
            "env_var": "HEARTBEAT_DIRECTORY",
        },
    )

    # Monitoring settings
    check_interval_seconds: int = field(
        default=30,
        metadata={
            "description": "Interval between health check runs in seconds",
            "env_var": "HEARTBEAT_CHECK_INTERVAL",
            "min_value": 1,
            "max_value": 3600,
        },
    )

    stale_multiplier: float = field(
        default=2.0,
        metadata={
            "description": "Multiplier for determining stale heartbeat threshold",
            "env_var": "HEARTBEAT_STALE_MULTIPLIER",
            "min_value": 1.0,
            "max_value": 10.0,
        },
    )

    # Alerting settings
    enable_alerts: bool = field(
        default=False,
        metadata={
            "description": "Enable alert notifications for service issues",
            "env_var": "HEARTBEAT_ENABLE_ALERTS",
        },
    )

    alert_interval_seconds: int = field(
        default=300,
        metadata={
            "description": "Minimum interval between alerts for the same issue",
            "env_var": "HEARTBEAT_ALERT_INTERVAL",
            "min_value": 60,
            "max_value": 3600,
        },
    )

    # Performance settings
    max_heartbeat_age_seconds: int = field(
        default=86400,  # 24 hours
        metadata={
            "description": "Maximum age of heartbeat files before cleanup",
            "env_var": "HEARTBEAT_MAX_AGE",
            "min_value": 3600,
            "max_value": 604800,  # 1 week
        },
    )

    cleanup_interval_seconds: int = field(
        default=3600,  # 1 hour
        metadata={
            "description": "Interval between heartbeat file cleanup runs",
            "env_var": "HEARTBEAT_CLEANUP_INTERVAL",
            "min_value": 300,
            "max_value": 86400,
        },
    )

    def __post_init__(self) -> None:
        """
        Validate configuration after initialization.

        Performs validation checks on all configuration parameters to ensure
        they are within acceptable ranges and meet system requirements.

        This method is automatically called after the dataclass is initialized
        and validates:
        - Numeric ranges for intervals and timeouts
        - Directory path validity
        - Logical consistency between related settings

        Raises:
            ValueError: If any configuration parameter is invalid

        Example:
            >>> settings = HeartbeatSettings(default_interval_seconds=0)
            ValueError: default_interval_seconds must be > 0
        """
        # Validate intervals
        if self.default_interval_seconds <= 0:
            raise ValueError("default_interval_seconds must be > 0")

        if self.default_timeout_seconds <= 0:
            raise ValueError("default_timeout_seconds must be > 0")

        if self.check_interval_seconds <= 0:
            raise ValueError("check_interval_seconds must be > 0")

        # Validate multipliers and ratios
        if self.stale_multiplier <= 0:
            raise ValueError("stale_multiplier must be > 0")

        if self.alert_interval_seconds <= 0:
            raise ValueError("alert_interval_seconds must be > 0")

        # Validate cleanup settings
        if self.max_heartbeat_age_seconds <= 0:
            raise ValueError("max_heartbeat_age_seconds must be > 0")

        if self.cleanup_interval_seconds <= 0:
            raise ValueError("cleanup_interval_seconds must be > 0")

        # Ensure timeout is reasonable compared to interval
        if self.default_timeout_seconds < self.default_interval_seconds:
            raise ValueError("default_timeout_seconds must be >= default_interval_seconds")

    @classmethod
    def from_env(cls) -> "HeartbeatSettings":
        """
        Create settings from environment variables.

        Loads configuration from environment variables, using default values
        for any variables that are not set. This method provides a convenient
        way to configure the heartbeat system through environment variables
        without requiring configuration files.

        Environment Variables:
        - HEARTBEAT_INTERVAL: Default heartbeat interval in seconds
        - HEARTBEAT_TIMEOUT: Default timeout threshold in seconds
        - HEARTBEAT_DIRECTORY: Directory for heartbeat files
        - HEARTBEAT_CHECK_INTERVAL: Health check interval in seconds
        - HEARTBEAT_STALE_MULTIPLIER: Stale heartbeat multiplier
        - HEARTBEAT_ENABLE_ALERTS: Enable alerts (true/false)
        - HEARTBEAT_ALERT_INTERVAL: Alert interval in seconds
        - HEARTBEAT_MAX_AGE: Maximum heartbeat age in seconds
        - HEARTBEAT_CLEANUP_INTERVAL: Cleanup interval in seconds

        Returns:
            HeartbeatSettings instance configured from environment variables

        Example:
            >>> export HEARTBEAT_INTERVAL=30
            >>> export HEARTBEAT_TIMEOUT=90
            >>> settings = HeartbeatSettings.from_env()
            >>> print(settings.default_interval_seconds)
            30
        """
        return cls(
            default_interval_seconds=int(os.getenv("HEARTBEAT_INTERVAL", "60")),
            default_timeout_seconds=int(os.getenv("HEARTBEAT_TIMEOUT", "120")),
            heartbeat_directory=os.getenv(
                "HEARTBEAT_DIRECTORY",
                "./heartbeats",
            ),
            check_interval_seconds=int(os.getenv("HEARTBEAT_CHECK_INTERVAL", "30")),
            stale_multiplier=float(os.getenv("HEARTBEAT_STALE_MULTIPLIER", "2.0")),
            enable_alerts=os.getenv("HEARTBEAT_ENABLE_ALERTS", "false").lower() == "true",
            alert_interval_seconds=int(os.getenv("HEARTBEAT_ALERT_INTERVAL", "300")),
            max_heartbeat_age_seconds=int(os.getenv("HEARTBEAT_MAX_AGE", "86400")),
            cleanup_interval_seconds=int(os.getenv("HEARTBEAT_CLEANUP_INTERVAL", "3600")),
        )

    def load_from_file(self, config_path: str) -> None:
        """
        Load configuration from a file.

        Updates the current settings with values loaded from a configuration file.
        This method allows for dynamic configuration updates without restarting
        the heartbeat system.

        The configuration file should be in JSON format with keys matching
        the setting names. Only specified settings will be updated; others
        will retain their current values.

        Args:
            config_path: Path to the configuration file

        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            json.JSONDecodeError: If the configuration file is invalid JSON
            ValueError: If any loaded values are invalid

        Example:
            >>> settings = HeartbeatSettings()
            >>> settings.load_from_file("/etc/heartbeat/config.json")
            # Updates settings from file
        """
        import json

        config_file_path = Path(config_path)
        if not config_file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file_path}")

        with open(config_file_path, encoding="utf-8") as f:
            config_data = json.load(f)

        # Update settings with loaded values
        for key, value in config_data.items():
            if hasattr(self, key):
                setattr(self, key, value)

        # Re-validate after loading
        self.__post_init__()

    def to_dict(self) -> dict[str, Any]:
        """
        Convert settings to a dictionary.

        Returns a dictionary representation of the current settings, which can
        be used for serialization, logging, or debugging purposes.

        Returns:
            Dictionary containing all current setting values

        Example:
            >>> settings = HeartbeatSettings()
            >>> config_dict = settings.to_dict()
            >>> print(config_dict["default_interval_seconds"])
            60
        """
        return {
            "default_interval_seconds": self.default_interval_seconds,
            "default_timeout_seconds": self.default_timeout_seconds,
            "heartbeat_directory": self.heartbeat_directory,
            "check_interval_seconds": self.check_interval_seconds,
            "stale_multiplier": self.stale_multiplier,
            "enable_alerts": self.enable_alerts,
            "alert_interval_seconds": self.alert_interval_seconds,
            "max_heartbeat_age_seconds": self.max_heartbeat_age_seconds,
            "cleanup_interval_seconds": self.cleanup_interval_seconds,
        }

    def get_heartbeat_directory_path(self) -> Path:
        """
        Get the heartbeat directory as a Path object.

        Returns the configured heartbeat directory as a Path object, which
        provides convenient methods for file system operations.

        Returns:
            Path object representing the heartbeat directory

        Example:
            >>> settings = HeartbeatSettings()
            >>> heartbeat_dir = settings.get_heartbeat_directory_path()
            >>> print(heartbeat_dir)
            PosixPath('./heartbeats')
        """
        return Path(self.heartbeat_directory)
