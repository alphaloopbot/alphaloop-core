"""Table handler for AlphaLoop Storage."""

from typing import Any, Literal

import pandas as pd
import polars as pl
from sqlalchemy import Column, Integer, MetaData, Table, text
from sqlalchemy.engine import Result

from ..exceptions import DatabaseQueryError, TableError
from .connection import DatabaseManager


class TableHandler:
    """Handles table operations and data retrieval."""

    def __init__(
        self,
        table_name: str,
        database_manager: DatabaseManager,
        columns: list[Column] | None = None,
        auto_id: bool = True,
    ) -> None:
        """Initialize table handler."""
        self.table_name = table_name
        self.database_manager = database_manager
        self.columns = columns or []
        self.auto_id = auto_id
        self.metadata = MetaData()
        self._table: Table | None = None
        self._sql_reader_converter: dict[str, Any] = {}

        self._initiate_sql_reader_converter()
        self._create_table_object()

    def _initiate_sql_reader_converter(self) -> None:
        """Initialize SQL reader converters for different output formats."""
        self._sql_reader_converter = {
            "list": self._read_sql_query_to_list,
            "pandas": self._read_sql_query_to_pandas,
            "polars": self._read_sql_query_to_polars,
        }

    def _create_table_object(self) -> None:
        """Create SQLAlchemy table object."""
        table_args = [self.table_name, self.metadata]

        if self.auto_id:
            table_args.append(
                Column("id", Integer, primary_key=True, autoincrement=True)
            )

        table_args.extend(self.columns)
        table_args.append({"extend_existing": True})

        self._table = Table(*table_args)

    @property
    def table(self) -> Table:
        """Get the SQLAlchemy table object."""
        if self._table is None:
            raise TableError(f"Table {self.table_name} not initialized")
        return self._table

    async def initialize_table(self) -> None:
        """Initialize table in database if it doesn't exist."""
        try:
            # Check if table exists using engine directly
            inspector = self.database_manager.async_engine.dialect.inspector(
                self.database_manager.async_engine
            )
            existing_tables = await inspector.get_table_names()

            if self.table_name not in existing_tables:
                await self.table.create(self.database_manager.async_engine)
        except Exception as e:
            raise TableError(
                f"Failed to initialize table {self.table_name}: {e}"
            ) from e

    async def execute_sql_query(self, query: str) -> Result:
        """Execute SQL query and return result."""
        try:
            async with self.database_manager.async_session() as session:
                result = await session.execute(text(query))
                await session.commit()
                return result
        except Exception as e:
            raise DatabaseQueryError(f"Failed to execute query: {query}\n{e}") from e

    def _read_sql_query_to_list(self, query: str) -> list[tuple]:
        """Execute SQL query and return result as list."""
        # Note: This is synchronous for compatibility with legacy code
        # In a full async implementation, this would be async
        with self.database_manager.sync_session_scope() as session:
            result = session.execute(text(query))
            return result.fetchall()

    def _read_sql_query_to_pandas(self, query: str) -> pd.DataFrame:
        """Execute SQL query and return result as pandas DataFrame."""
        with self.database_manager.sync_session_scope() as session:
            return pd.read_sql(sql=query, con=session.connection())

    def _read_sql_query_to_polars(self, query: str) -> pl.DataFrame:
        """Execute SQL query and return result as polars DataFrame."""
        with self.database_manager.sync_session_scope() as session:
            return pl.read_database(query=query, connection=session)

    async def get_columns(self) -> list[str]:
        """Get table column names."""
        query = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{self.table_name}'
            ORDER BY ordinal_position;
        """
        result = await self.execute_sql_query(query)
        return [row[0] for row in result.fetchall()]

    async def get_unique_values(self, column_name: str) -> list[Any]:
        """Get unique values from a column."""
        query = f"SELECT DISTINCT {column_name} FROM {self.table_name};"
        result = await self.execute_sql_query(query)
        return [row[0] for row in result.fetchall()]

    async def get_last_timestamp_id(
        self, timestamp_column: str = "timestamp_id"
    ) -> int | None:
        """Get the last timestamp ID from the table."""
        query = f"SELECT MAX({timestamp_column}) FROM {self.table_name};"
        result = await self.execute_sql_query(query)
        value = result.fetchone()[0]
        return value if value is not None else None

    async def get_last_timestamp_data(
        self,
        timestamp_column: str = "timestamp_id",
        output_type: Literal["list", "pandas", "polars"] = "list",
    ) -> list[tuple] | pd.DataFrame | pl.DataFrame:
        """Get records with the last timestamp ID."""
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE {timestamp_column} = (
                SELECT MAX({timestamp_column}) FROM {self.table_name}
            );
        """
        return self._sql_reader_converter[output_type](query)

    async def get_all_data(
        self, output_type: Literal["list", "pandas", "polars"] = "list"
    ) -> list[tuple] | pd.DataFrame | pl.DataFrame:
        """Get all data from the table."""
        query = f"SELECT * FROM {self.table_name};"
        return self._sql_reader_converter[output_type](query)

    async def get_data_by_interval(
        self,
        column_name: str,
        values_interval: tuple,
        metadata_id: int | None = None,
        output_type: Literal["list", "pandas", "polars"] = "list",
    ) -> list[tuple] | pd.DataFrame | pl.DataFrame:
        """Get data within an interval."""
        value_interval_start = min(values_interval)
        value_interval_end = max(values_interval)

        if metadata_id is None:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE {column_name} BETWEEN {value_interval_start} AND {value_interval_end};
            """
        else:
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE {column_name} BETWEEN {value_interval_start} AND {value_interval_end}
                AND metadata_id = {metadata_id};
            """

        return self._sql_reader_converter[output_type](query)

    async def get_data_by_id(
        self, record_id: int, output_type: Literal["list", "pandas", "polars"] = "list"
    ) -> list[tuple] | pd.DataFrame | pl.DataFrame:
        """Get data by record ID."""
        query = f"SELECT * FROM {self.table_name} WHERE id = {record_id};"
        return self._sql_reader_converter[output_type](query)

    async def insert_data(self, data: dict[str, Any]) -> int:
        """Insert data into table and return the inserted ID."""
        try:
            async with self.database_manager.async_session() as session:
                result = await session.execute(self.table.insert().values(**data))
                await session.commit()
                return (
                    result.inserted_primary_key[0]
                    if result.inserted_primary_key
                    else None
                )
        except Exception as e:
            raise TableError(
                f"Failed to insert data into {self.table_name}: {e}"
            ) from e

    async def update_data(self, record_id: int, data: dict[str, Any]) -> bool:
        """Update data in table."""
        try:
            async with self.database_manager.async_session() as session:
                result = await session.execute(
                    self.table.update()
                    .where(self.table.c.id == record_id)
                    .values(**data)
                )
                await session.commit()
                return result.rowcount > 0
        except Exception as e:
            raise TableError(f"Failed to update data in {self.table_name}: {e}") from e

    async def delete_data(self, record_id: int) -> bool:
        """Delete data from table."""
        try:
            async with self.database_manager.async_session() as session:
                result = await session.execute(
                    self.table.delete().where(self.table.c.id == record_id)
                )
                await session.commit()
                return result.rowcount > 0
        except Exception as e:
            raise TableError(
                f"Failed to delete data from {self.table_name}: {e}"
            ) from e

    async def get_table_info(self) -> dict[str, Any]:
        """Get table information."""
        try:
            async with self.database_manager.async_session() as session:
                # Get row count
                count_result = await session.execute(
                    text(f"SELECT COUNT(*) FROM {self.table_name}")
                )
                row_count = count_result.fetchone()[0]

                # Get table size
                size_result = await session.execute(
                    text(
                        f"""
                        SELECT pg_size_pretty(pg_total_relation_size('{self.table_name}'))
                    """
                    )
                )
                table_size = size_result.fetchone()[0]

                # Get columns
                columns = await self.get_columns()

                return {
                    "table_name": self.table_name,
                    "row_count": row_count,
                    "table_size": table_size,
                    "columns": columns,
                    "auto_id": self.auto_id,
                }
        except Exception as e:
            raise TableError(
                f"Failed to get table info for {self.table_name}: {e}"
            ) from e
