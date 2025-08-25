"""Table handler for AlphaLoop Storage."""

from typing import Any

import pandas as pd
import polars as pl
import sqlalchemy
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    text,
)
from sqlalchemy.exc import NoSuchTableError

from infrastructure.alphaloop_storage.exceptions import TableError

from .connection import DatabaseManager
from .schema_generator import SchemaGenerator


class TableHandler:
    """Handles table operations with automatic schema creation from YAML."""

    def __init__(
        self,
        table_name: str,
        database_manager: DatabaseManager,
        auto_id: bool = True,
        columns: list[Column] | None = None,
    ):
        """Initialize table handler.

        Args:
            table_name: Name of the table to handle.
            database_manager: Database manager instance.
            auto_id: Whether to automatically add an ID column.
            columns: Additional columns to add to the table.
        """
        self.table_name = table_name
        self.database_manager = database_manager
        self.auto_id = auto_id
        self.columns = columns or []
        self.metadata = MetaData()
        self._table = None
        self._schema_generator = SchemaGenerator()

    def _ensure_table_exists(self) -> None:
        """Ensure the table exists, creating it from YAML schema if needed."""
        try:
            # Try to reflect the existing table
            self._table = Table(
                self.table_name,
                self.metadata,
                autoload_with=self.database_manager.sync_engine,
                extend_existing=True,
            )
            # Table exists, we're done
            return
        except NoSuchTableError:
            # Table doesn't exist, create it from YAML schema
            self._create_table_from_schema()
        except Exception as e:
            # Other error, try to create from schema anyway
            print(f"Warning: Could not reflect table {self.table_name}: {e}")
            self._create_table_from_schema()

    def _create_table_from_schema(self) -> None:
        """Create table from YAML schema definition."""
        try:
            # Load schema and find our table
            schema = self._schema_generator.load_schema()

            # Find the table definition in the schema
            table_spec = None
            for _db_name, db_spec in schema["databases"].items():
                if self.table_name in db_spec["tables"]:
                    table_spec = db_spec["tables"][self.table_name]
                    break

            if not table_spec:
                raise TableError(f"Table '{self.table_name}' not found in YAML schema")

            # Create the table using the schema generator
            self._create_table_from_spec(table_spec)

        except Exception as e:
            raise TableError(f"Failed to create table '{self.table_name}' from schema: {e}") from e

    def _create_table_from_spec(self, table_spec: dict[str, Any]) -> None:
        """Create table from table specification."""
        # Generate columns from YAML spec
        columns = []

        for col_spec in table_spec["columns"]:
            col_name = col_spec["name"]
            col_type = col_spec["type"]

            # Map YAML types to SQLAlchemy types
            if col_type == "Integer":
                sqlalchemy_type = Integer
            elif col_type == "Float":
                sqlalchemy_type = Numeric(20, 8)
            elif col_type == "String":
                sqlalchemy_type = String(255)
            elif col_type == "Boolean":
                sqlalchemy_type = sqlalchemy.Boolean
            elif col_type == "TIMESTAMP":
                sqlalchemy_type = DateTime
            elif col_type == "JSON":
                sqlalchemy_type = sqlalchemy.JSON
            else:
                sqlalchemy_type = String(255)  # Default fallback

            # Handle primary key
            if col_spec.get("primary_key"):
                if col_type == "Integer":
                    columns.append(Column(col_name, Integer, primary_key=True, autoincrement=True))
                else:
                    columns.append(Column(col_name, sqlalchemy_type, primary_key=True))
            else:
                # Handle foreign key
                if "foreign_key" in col_spec:
                    # TODO: Implement foreign key handling
                    columns.append(Column(col_name, sqlalchemy_type, nullable=False))
                else:
                    # Handle nullable
                    nullable = col_spec.get("nullable", True)
                    columns.append(Column(col_name, sqlalchemy_type, nullable=nullable))

        # Create the table
        self._table = Table(
            self.table_name,
            self.metadata,
            *columns,
            extend_existing=True,
        )

        # Create the table in the database
        self._table.create(self.database_manager.sync_engine, checkfirst=True)

        # Create indexes if needed
        self._create_indexes_from_spec(table_spec)

    def _create_indexes_from_spec(self, table_spec: dict[str, Any]) -> None:
        """Create indexes based on table specification."""
        if table_spec.get("type") == "data":
            # Create common indexes for data tables
            indexes = [
                f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_timestamp ON "
                f"{self.table_name}(timestamp_id);",
                f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_metadata_id ON "
                f"{self.table_name}(metadata_id);",
                f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_metadata_timestamp ON "
                f"{self.table_name}(metadata_id, timestamp_id);",
            ]

            for index_sql in indexes:
                try:
                    self.database_manager.sync_engine.execute(text(index_sql))
                except Exception as e:
                    print(f"Warning: Could not create index: {e}")

    @property
    def table(self) -> Table:
        """Get the SQLAlchemy table object."""
        if self._table is None:
            # Try to ensure table exists (will create from YAML if needed)
            self._ensure_table_exists()

            if self._table is None:
                raise TableError(f"Failed to create or reflect table {self.table_name}")

        return self._table

    async def insert_data(
        self, data: dict[str, Any] | list[dict[str, Any]]
    ) -> int | list[int] | list[None] | None:
        """Insert data into table and return the inserted ID(s)."""
        try:
            # Ensure table exists before inserting
            self._ensure_table_exists()

            session = self.database_manager.async_session()
            async with session as session:
                if isinstance(data, dict):
                    # Single record insert
                    result = await session.execute(self.table.insert().values(**data))
                    await session.commit()
                    return result.inserted_primary_key[0] if result.inserted_primary_key else None
                elif isinstance(data, list):
                    # Bulk insert
                    if not data:
                        return []

                    # Insert all records
                    result = await session.execute(self.table.insert().values(data))
                    await session.commit()

                    # Return list of inserted IDs if available
                    if result.inserted_primary_key:
                        return result.inserted_primary_key
                    else:
                        # If we can't get the IDs, return a list of None values
                        return [None] * len(data)
                else:
                    raise ValueError(f"Data must be dict or list[dict], got {type(data)}")
        except Exception as e:
            raise TableError(f"Failed to insert data into {self.table_name}: {e}") from e

    async def query_data(
        self,
        filters: dict[str, Any] | None = None,
        limit: int | None = None,
        order_by: str | None = None,
    ) -> list[dict[str, Any]]:
        """Query data from table."""
        try:
            # Ensure table exists before querying
            self._ensure_table_exists()

            session = self.database_manager.async_session()
            async with session as session:
                query = self.table.select()

                if filters:
                    for column, value in filters.items():
                        if hasattr(self.table.c, column):
                            query = query.where(getattr(self.table.c, column) == value)

                if order_by:
                    if hasattr(self.table.c, order_by):
                        query = query.order_by(getattr(self.table.c, order_by))

                if limit:
                    query = query.limit(limit)

                result = await session.execute(query)
                rows = result.fetchall()

                return [dict(row._mapping) for row in rows]
        except Exception as e:
            raise TableError(f"Failed to query data from {self.table_name}: {e}") from e

    async def update_data(self, filters: dict[str, Any], updates: dict[str, Any]) -> int:
        """Update data in table."""
        try:
            # Ensure table exists before updating
            self._ensure_table_exists()

            session = self.database_manager.async_session()
            async with session as session:
                query = self.table.update()

                for column, value in filters.items():
                    if hasattr(self.table.c, column):
                        query = query.where(getattr(self.table.c, column) == value)

                result = await session.execute(query.values(**updates))
                await session.commit()

                return result.rowcount
        except Exception as e:
            raise TableError(f"Failed to update data in {self.table_name}: {e}") from e

    async def delete_data(self, filters: dict[str, Any]) -> int:
        """Delete data from table."""
        try:
            # Ensure table exists before deleting
            self._ensure_table_exists()

            session = self.database_manager.async_session()
            async with session as session:
                query = self.table.delete()

                for column, value in filters.items():
                    if hasattr(self.table.c, column):
                        query = query.where(getattr(self.table.c, column) == value)

                result = await session.execute(query)
                await session.commit()

                return result.rowcount
        except Exception as e:
            raise TableError(f"Failed to delete data from {self.table_name}: {e}") from e

    def to_pandas(self, query: str) -> pd.DataFrame:
        """Execute query and return results as pandas DataFrame."""
        try:
            return pd.read_sql(query, self.database_manager.sync_engine)
        except Exception as e:
            raise TableError(f"Failed to execute query on {self.table_name}: {e}") from e

    def to_polars(self, query: str) -> pl.DataFrame:
        """Execute query and return results as polars DataFrame."""
        try:
            return pl.read_database(query, self.database_manager.sync_engine)
        except Exception as e:
            raise TableError(f"Failed to execute query on {self.table_name}: {e}") from e
