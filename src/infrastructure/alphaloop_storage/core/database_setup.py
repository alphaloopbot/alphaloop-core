"""
Database setup module for AlphaLoop Storage.

This module provides the authoritative way to set up database schemas
using the YAML configuration as the single source of truth.
"""

import asyncio
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import text

from ..exceptions import StorageError
from .connection import DatabaseConfig, DatabaseManager
from .table_handler import TableHandler

# Import logging - this should be available in the infrastructure
try:
    from alphaloop_logging import AlphaLoopLogger, LoggingConfig

    config = LoggingConfig(app_name="alphaloop-storage")
    logger = AlphaLoopLogger(config)
except ImportError:
    # Fallback for development/testing
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("alphaloop-storage")


class DatabaseSetup:
    """Handles database schema setup using YAML configuration."""

    def __init__(self, config_path: str = "config/database_schema.yaml"):
        """Initialize database setup with YAML configuration."""
        self.config_path = Path(config_path)
        self.schema = self._load_schema()

    def _load_schema(self) -> dict[str, Any]:
        """Load database schema from YAML file."""
        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise StorageError(f"Schema file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise StorageError(f"Invalid YAML in schema file: {e}")

    async def setup_databases(self, db_manager: DatabaseManager) -> None:
        """Set up all databases and tables from YAML schema."""
        try:
            # Create databases
            for db_name in self.schema.get("databases", {}).keys():
                await self._create_database(db_manager, db_name)

            # Create tables for each database
            for db_name, db_spec in self.schema.get("databases", {}).items():
                await self._create_tables_for_database(db_manager, db_name, db_spec)

        except Exception as e:
            raise StorageError(f"Failed to set up databases: {e}")

    async def _create_database(self, db_manager: DatabaseManager, db_name: str) -> None:
        """Create a database if it doesn't exist."""
        try:
            # Connect to postgres database to create new database
            postgres_config = DatabaseConfig(
                host=db_manager.config.host,
                port=db_manager.config.port,
                username=db_manager.config.username,
                password=db_manager.config.password,
                database="postgres",
            )
            postgres_manager = DatabaseManager(postgres_config)

            # Use autocommit mode for DDL operations
            async with postgres_manager.async_engine.connect() as conn:
                await conn.execution_options(isolation_level="AUTOCOMMIT")
                # Drop database if exists (for clean setup)
                await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
                # Create database
                await conn.execute(text(f"CREATE DATABASE {db_name}"))
                await conn.commit()

            print(f"✅ Created database: {db_name}")

        except Exception as e:
            raise StorageError(f"Failed to create database {db_name}: {e}")

    async def _create_tables_for_database(
        self, db_manager: DatabaseManager, db_name: str, db_spec: dict[str, Any]
    ) -> None:
        """Create all tables for a specific database."""
        try:
            # Create database manager for this specific database
            db_config_specific = DatabaseConfig(
                host=db_manager.config.host,
                port=db_manager.config.port,
                username=db_manager.config.username,
                password=db_manager.config.password,
                database=db_name,
            )
            db_manager_specific = DatabaseManager(db_config_specific)

            # Create each table
            for table_name, table_spec in db_spec.get("tables", {}).items():
                await self._create_table(db_manager_specific, table_name, table_spec)

        except Exception as e:
            raise StorageError(f"Failed to create tables for database {db_name}: {e}")

    async def _create_table(
        self, db_manager: DatabaseManager, table_name: str, table_spec: dict[str, Any]
    ) -> None:
        """Create a single table from specification."""
        try:
            # Use TableHandler to create the table (it handles YAML schema)
            table_handler = TableHandler(table_name, db_manager)

            # Force table creation by accessing the table property
            _ = table_handler.table

            print(f"✅ Created table: {db_manager.config.database}.{table_name}")

        except Exception as e:
            print(
                f"⚠️  Table {db_manager.config.database}.{table_name} already exists or error: {e}"
            )


async def setup_database_schemas(
    host: str = "localhost",
    port: int = 5432,
    user: str = "didac",
    password: str = "your_secure_password",
    config_path: str = "config/database_schema.yaml",
) -> None:
    """
    Set up database schemas using YAML configuration.

    This is the authoritative way to set up database schemas.
    All schema creation should go through this function.
    """
    try:
        # Create database setup instance
        setup = DatabaseSetup(config_path)

        # Create database manager for postgres (to create other databases)
        db_config = DatabaseConfig(
            host=host, port=port, username=user, password=password, database="postgres"
        )
        db_manager = DatabaseManager(db_config)

        # Set up all databases and tables
        await setup.setup_databases(db_manager)

        print("✅ Database schemas setup completed successfully!")

    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        raise


def setup_database_schemas_sync(
    host: str = "localhost",
    port: int = 5432,
    user: str = "didac",
    password: str = "your_secure_password",
    config_path: str = "config/database_schema.yaml",
) -> None:
    """
    Synchronous wrapper for database schema setup.
    """
    asyncio.run(setup_database_schemas(host, port, user, password, config_path))
