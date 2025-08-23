"""AlphaLoop Storage Package

Provides unified data storage and management layer for AlphaLoop systems.
"""

__version__ = "0.1.0"
__author__ = "Didac Cristobal-Canals"
__email__ = "didac.crst@gmail.com"

from .core.connection import DatabaseConfig, DatabaseManager, create_database_manager
from .core.schema_manager import ColumnDefinition, SchemaManager, TableDefinition
from .core.table_handler import TableHandler
from .models.base import Base, BaseModel
from .utils.query_builder import QueryBuilder

__all__ = [
    "DatabaseConfig",
    "DatabaseManager",
    "create_database_manager",
    "TableHandler",
    "SchemaManager",
    "TableDefinition",
    "ColumnDefinition",
    "Base",
    "BaseModel",
    "QueryBuilder",
]
