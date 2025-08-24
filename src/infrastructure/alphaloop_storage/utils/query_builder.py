"""Query builder utilities for AlphaLoop Storage."""

from typing import Any


class QueryBuilder:
    """Utility class for building SQL queries."""

    def __init__(self, table_name: str) -> None:
        """Initialize query builder with table name."""
        self.table_name = table_name
        self._select_columns: list[str] = ["*"]
        self._where_conditions: list[str] = []
        self._order_by: list[str] = []
        self._limit: int | None = None
        self._offset: int | None = None

    def select(self, columns: str | list[str]) -> "QueryBuilder":
        """Set columns to select."""
        if isinstance(columns, str):
            self._select_columns = [columns]
        else:
            self._select_columns = columns
        return self

    def where(self, condition: str) -> "QueryBuilder":
        """Add WHERE condition."""
        self._where_conditions.append(condition)
        return self

    def where_equals(self, column: str, value: Any) -> "QueryBuilder":
        """Add WHERE condition for equality."""
        if isinstance(value, str):
            condition = f"{column} = '{value}'"
        else:
            condition = f"{column} = {value}"
        return self.where(condition)

    def where_in(self, column: str, values: list[Any]) -> "QueryBuilder":
        """Add WHERE IN condition."""
        if not values:
            return self

        formatted_values = []
        for value in values:
            if isinstance(value, str):
                formatted_values.append(f"'{value}'")
            else:
                formatted_values.append(str(value))

        condition = f"{column} IN ({', '.join(formatted_values)})"
        return self.where(condition)

    def where_between(self, column: str, start: Any, end: Any) -> "QueryBuilder":
        """Add WHERE BETWEEN condition."""
        condition = f"{column} BETWEEN {start} AND {end}"
        return self.where(condition)

    def where_like(self, column: str, pattern: str) -> "QueryBuilder":
        """Add WHERE LIKE condition."""
        condition = f"{column} LIKE '{pattern}'"
        return self.where(condition)

    def order_by(self, column: str, direction: str = "ASC") -> "QueryBuilder":
        """Add ORDER BY clause."""
        self._order_by.append(f"{column} {direction.upper()}")
        return self

    def limit(self, limit: int) -> "QueryBuilder":
        """Set LIMIT clause."""
        self._limit = limit
        return self

    def offset(self, offset: int) -> "QueryBuilder":
        """Set OFFSET clause."""
        self._offset = offset
        return self

    def build(self) -> str:
        """Build the SQL query."""
        query_parts = ["SELECT", ", ".join(self._select_columns)]
        query_parts.append(f"FROM {self.table_name}")

        if self._where_conditions:
            query_parts.append("WHERE " + " AND ".join(self._where_conditions))

        if self._order_by:
            query_parts.append("ORDER BY " + ", ".join(self._order_by))

        if self._limit is not None:
            query_parts.append(f"LIMIT {self._limit}")

        if self._offset is not None:
            query_parts.append(f"OFFSET {self._offset}")

        return " ".join(query_parts) + ";"

    def reset(self) -> "QueryBuilder":
        """Reset the query builder to initial state."""
        self._select_columns = ["*"]
        self._where_conditions = []
        self._order_by = []
        self._limit = None
        self._offset = None
        return self

    @classmethod
    def create_select_query(
        cls,
        table_name: str,
        columns: list[str] | None = None,
        where_conditions: dict[str, Any] | None = None,
        order_by: list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> str:
        """Create a SELECT query with all parameters."""
        builder = cls(table_name)

        if columns:
            builder.select(columns)

        if where_conditions:
            for column, value in where_conditions.items():
                if isinstance(value, list):
                    builder.where_in(column, value)
                elif isinstance(value, tuple):
                    builder.where_in(column, list(value))
                else:
                    builder.where_equals(column, value)

        if order_by:
            for order_clause in order_by:
                if " " in order_clause:
                    column, direction = order_clause.rsplit(" ", 1)
                    builder.order_by(column, direction)
                else:
                    builder.order_by(order_clause)

        if limit:
            builder.limit(limit)

        if offset:
            builder.offset(offset)

        return builder.build()

    @classmethod
    def create_insert_query(cls, table_name: str, data: dict[str, Any]) -> tuple[str, list[Any]]:
        """Create an INSERT query with parameterized values."""
        columns = list(data.keys())
        placeholders = [f"${i+1}" for i in range(len(columns))]
        values = list(data.values())

        query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING id;
        """

        return query, values

    @classmethod
    def create_update_query(
        cls, table_name: str, data: dict[str, Any], where_conditions: dict[str, Any]
    ) -> tuple[str, list[Any]]:
        """Create an UPDATE query with parameterized values."""
        set_clauses = [f"{column} = ${i+1}" for i, column in enumerate(data.keys())]
        where_clauses = []
        values = list(data.values())

        start_param = len(values) + 1
        for column, value in where_conditions.items():
            where_clauses.append(f"{column} = ${start_param}")
            values.append(value)
            start_param += 1

        query = f"""
            UPDATE {table_name}
            SET {', '.join(set_clauses)}
            WHERE {' AND '.join(where_clauses)}
            RETURNING id;
        """

        return query, values

    @classmethod
    def create_delete_query(
        cls, table_name: str, where_conditions: dict[str, Any]
    ) -> tuple[str, list[Any]]:
        """Create a DELETE query with parameterized values."""
        where_clauses = []
        values = []

        for i, (column, value) in enumerate(where_conditions.items()):
            where_clauses.append(f"{column} = ${i+1}")
            values.append(value)

        query = f"""
            DELETE FROM {table_name}
            WHERE {' AND '.join(where_clauses)}
            RETURNING id;
        """

        return query, values
