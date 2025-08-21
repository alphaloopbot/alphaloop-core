"""Configuration settings for heartbeat monitoring."""

import json
from pathlib import Path
from typing import Any


class HeartbeatSettings:
    """Configuration settings for heartbeat monitoring."""

    def __init__(self) -> None:
        """Initialize default settings."""
        self.check_interval_seconds = 30
        self.default_interval_seconds = 60
        self.stale_multiplier = 2.0
        self.enable_alerts = False
        self.heartbeat_directory = "/tmp/heartbeats"
        self.alert_config: dict[str, Any] = {}

    def load_from_file(self, config_path: str) -> None:
        """Load settings from a configuration file."""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_file) as f:
            config_data = json.load(f)

        self.check_interval_seconds = config_data.get("check_interval_seconds", 30)
        self.default_interval_seconds = config_data.get("default_interval_seconds", 60)
        self.stale_multiplier = config_data.get("stale_multiplier", 2.0)
        self.enable_alerts = config_data.get("enable_alerts", False)
        self.heartbeat_directory = config_data.get("heartbeat_directory", "/tmp/heartbeats")
        self.alert_config = config_data.get("alert_config", {})

    def to_dict(self) -> dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "check_interval_seconds": self.check_interval_seconds,
            "default_interval_seconds": self.default_interval_seconds,
            "stale_multiplier": self.stale_multiplier,
            "enable_alerts": self.enable_alerts,
            "heartbeat_directory": self.heartbeat_directory,
            "alert_config": self.alert_config,
        }
