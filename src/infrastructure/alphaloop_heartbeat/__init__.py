"""AlphaLoop Heartbeat - Health monitoring and status checking functionality."""

__version__ = "0.1.0"
__author__ = "Didac Cristobal-Canals"
__email__ = "didac.crst@gmail.com"

from .config.settings import HeartbeatSettings
from .core.heartbeat_checker import HeartbeatChecker
from .core.heartbeat_generator import HeartbeatGenerator

__all__ = [
    "HeartbeatGenerator",
    "HeartbeatChecker",
    "HeartbeatSettings",
]
