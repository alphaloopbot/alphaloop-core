"""Schema management for AlphaLoop Storage."""

from typing import Any

from infrastructure.alphaloop_storage.exceptions import SchemaError
from pydantic import BaseModel


class ColumnDefinition(BaseModel):
    """Definition of a database column."""

    name: str
    type: str
    nullable: bool = True
    primary_key: bool = False
    autoincrement: bool = False
    default: Any | None = None
    unique: bool = False
    index: bool = False


class TableDefinition(BaseModel):
    """Definition of a database table."""

    name: str
    columns: list[ColumnDefinition]
    auto_id: bool = True
    metadata_table: str | None = None
    reporting: bool = False
    parent_table: str | None = None


class SchemaManager:
    """Manages database schemas and table definitions."""

    def __init__(self) -> None:
        """Initialize schema manager."""
        self._tables: dict[str, TableDefinition] = {}

    def register_table(self, table_def: TableDefinition) -> None:
        """Register a table definition."""
        self._tables[table_def.name] = table_def

    def get_table(self, table_name: str) -> TableDefinition | None:
        """Get table definition by name."""
        return self._tables.get(table_name)

    def list_tables(self) -> list[str]:
        """List all registered table names."""
        return list(self._tables.keys())

    def validate_table(self, table_name: str) -> bool:
        """Validate that a table definition exists and is complete."""
        if table_name not in self._tables:
            return False

        table_def = self._tables[table_name]

        # Check that table has at least one column
        if not table_def.columns:
            return False

        # Check that column names are unique
        column_names = [col.name for col in table_def.columns]
        if len(column_names) != len(set(column_names)):
            return False

        return True

    def get_table_schema(self, table_name: str) -> dict[str, Any]:
        """Get table schema as dictionary."""
        table_def = self.get_table(table_name)
        if not table_def:
            raise SchemaError(f"Table '{table_name}' not found")

        return {
            "name": table_def.name,
            "columns": [col.dict() for col in table_def.columns],
            "auto_id": table_def.auto_id,
            "metadata_table": table_def.metadata_table,
            "reporting": table_def.reporting,
            "parent_table": table_def.parent_table,
        }

    def export_schema(self) -> dict[str, Any]:
        """Export all table schemas."""
        return {"tables": {name: self.get_table_schema(name) for name in self.list_tables()}}

    def import_schema(self, schema_data: dict[str, Any]) -> None:
        """Import table schemas from dictionary."""
        if "tables" not in schema_data:
            raise SchemaError("Invalid schema format: missing 'tables' key")

        for table_data in schema_data["tables"].values():
            # Convert column data back to ColumnDefinition objects
            columns = [ColumnDefinition(**col_data) for col_data in table_data.get("columns", [])]

            table_def = TableDefinition(
                name=table_data["name"],
                columns=columns,
                auto_id=table_data.get("auto_id", True),
                metadata_table=table_data.get("metadata_table"),
                reporting=table_data.get("reporting", False),
                parent_table=table_data.get("parent_table"),
            )

            self.register_table(table_def)

    def create_sql_ddl(self, table_name: str) -> str:
        """Generate SQL DDL for table creation."""
        table_def = self.get_table(table_name)
        if not table_def:
            raise SchemaError(f"Table '{table_name}' not found")

        # Start building CREATE TABLE statement
        ddl_parts = [f"CREATE TABLE {table_name} ("]

        column_definitions = []

        # Add auto-incrementing ID if enabled
        if table_def.auto_id:
            column_definitions.append("id SERIAL PRIMARY KEY")

        # Add user-defined columns
        for column in table_def.columns:
            col_def = f"{column.name} {column.type}"

            if not column.nullable:
                col_def += " NOT NULL"

            if column.primary_key:
                col_def += " PRIMARY KEY"

            if column.unique:
                col_def += " UNIQUE"

            if column.default is not None:
                if isinstance(column.default, str):
                    col_def += f" DEFAULT '{column.default}'"
                else:
                    col_def += f" DEFAULT {column.default}"

            column_definitions.append(col_def)

        ddl_parts.append(", ".join(column_definitions))
        ddl_parts.append(");")

        return " ".join(ddl_parts)

    def get_dependent_tables(self, table_name: str) -> list[str]:
        """Get tables that depend on the specified table."""
        dependent_tables = []

        for name, table_def in self._tables.items():
            if table_def.metadata_table == table_name or table_def.parent_table == table_name:
                dependent_tables.append(name)

        return dependent_tables

    def get_table_hierarchy(self) -> dict[str, list[str]]:
        """Get table hierarchy showing parent-child relationships."""
        hierarchy = {}

        for table_name in self.list_tables():
            table_def = self.get_table(table_name)
            if table_def:
                children = self.get_dependent_tables(table_name)
                if children:
                    hierarchy[table_name] = children

        return hierarchy
