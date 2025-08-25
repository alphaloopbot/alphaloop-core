"""AlphaLoop Cache Package

Provides Redis/Valkey caching and pub/sub functionality for AlphaLoop systems.
"""

__version__ = "0.1.0"
__author__ = "Didac Cristobal-Canals"
__email__ = "didac.crst@gmail.com"

from .core.connection import CacheConfig, CacheManager, create_cache_manager
from .core.generic_cache import GenericCache
from .core.pubsub import PubSubManager, PubSubMessage
from .models.cache_entry import CacheEntry
from .utils.key_builder import KeyBuilder

__all__ = [
    "CacheConfig",
    "CacheManager",
    "create_cache_manager",
    "GenericCache",
    "PubSubManager",
    "PubSubMessage",
    "CacheEntry",
    "KeyBuilder",
]
