"""AlphaLoop Core - A modern Python project with enterprise-grade tooling."""

__version__ = "0.1.0"
__author__ = "Didac Cristobal-Canals"
__email__ = "didac.crst@gmail.com"

# Export service factory and package configurations
from .shared.utils.package_config import (
    get_all_package_configs,
    get_cache_config,
    get_heartbeat_config,
    get_logging_config,
    get_security_config,
    get_storage_config,
)
from .shared.utils.service_factory import service_factory

__all__ = [
    "service_factory",
    "get_cache_config",
    "get_heartbeat_config",
    "get_logging_config",
    "get_security_config",
    "get_storage_config",
    "get_all_package_configs",
]
