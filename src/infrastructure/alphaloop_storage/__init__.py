"""
AlphaLoop Storage Infrastructure Package.

This package provides database storage capabilities for the AlphaLoop system.
"""

__version__ = "0.1.0"
__author__ = "Didac Cristobal-Canals"
__email__ = "didac.crst@gmail.com"

from .core.connection import DatabaseConfig, DatabaseManager, create_database_manager
from .core.database_setup import setup_database_schemas, setup_database_schemas_sync
from .core.table_handler import TableHandler
from .exceptions import StorageError

__all__ = [
    "DatabaseManager",
    "DatabaseConfig",
    "create_database_manager",
    "TableHandler",
    "setup_database_schemas",
    "setup_database_schemas_sync",
    "StorageError",
]
