"""
Database Schema Generator for AlphaLoop Storage

This module provides functionality to generate SQL DDL from YAML schema configurations.
It ensures we have a single source of truth for database schemas.
"""

from typing import Any

import yaml


class SchemaGenerator:
    """Generates SQL DDL from YAML schema configurations."""

    def __init__(self, yaml_path: str | None = None):
        """Initialize the schema generator.

        Args:
            yaml_path: Path to the YAML schema file. If None, uses default path.
        """
        self.yaml_path = yaml_path or "config/database_schema.yaml"
        self._type_mapping = {
            "Integer": "INTEGER",
            "Float": "DECIMAL(20,8)",
            "String": "VARCHAR(255)",
            "Boolean": "BOOLEAN",
            "TIMESTAMP": "TIMESTAMP",
            "JSON": "JSONB",
        }

    def load_schema(self) -> dict[str, Any]:
        """Load the YAML schema configuration.

        Returns:
            Dictionary containing the schema configuration.

        Raises:
            FileNotFoundError: If the YAML file doesn't exist.
            yaml.YAMLError: If the YAML file is malformed.
        """
        try:
            with open(self.yaml_path) as file:
                return yaml.safe_load(file)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Schema file not found: {self.yaml_path}") from e
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in schema file: {e}") from e

    def _generate_column_sql(self, column: dict[str, Any]) -> str:
        """Generate SQL column definition from YAML column spec.

        Args:
            column: Column specification from YAML.

        Returns:
            SQL column definition string.
        """
        name = column["name"]
        col_type = column["type"]

        sql_type = str(self._type_mapping.get(col_type, col_type))

        # Handle primary key
        if column.get("primary_key"):
            if col_type == "Integer":
                sql_type = "INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY"
            else:
                sql_type += " PRIMARY KEY"

        # Handle foreign key
        if "foreign_key" in column:
            fk_ref = str(column["foreign_key"])
            sql_type += f" REFERENCES {fk_ref}"

        # Handle nullable
        if not column.get("primary_key") and not column.get("nullable", True):
            sql_type += " NOT NULL"

        return f"    {name} {sql_type}"

    def _generate_table_sql(self, table_name: str, table_spec: dict[str, Any]) -> str:
        """Generate SQL CREATE TABLE statement from YAML table spec.

        Args:
            table_name: Name of the table.
            table_spec: Table specification from YAML.

        Returns:
            SQL CREATE TABLE statement.
        """
        columns = [self._generate_column_sql(col) for col in table_spec["columns"]]
        return f"CREATE TABLE {table_name} (\n" + ",\n".join(columns) + "\n);"

    def _generate_indexes(self, table_name: str, table_spec: dict[str, Any]) -> list[str]:
        """Generate SQL CREATE INDEX statements.

        Args:
            table_name: Name of the table.
            table_spec: Table specification from YAML.

        Returns:
            List of SQL CREATE INDEX statements.
        """
        indexes = []

        # Common indexes based on table type
        if table_spec.get("type") == "data":
            # Data tables typically need timestamp and metadata_id indexes
            indexes.extend(
                [
                    f"CREATE INDEX idx_{table_name}_timestamp ON {table_name}(timestamp_id);",
                    f"CREATE INDEX idx_{table_name}_metadata_id ON {table_name}(metadata_id);",
                    f"CREATE INDEX idx_{table_name}_metadata_timestamp ON {table_name}(metadata_id, timestamp_id);",
                ]
            )

        elif table_spec.get("type") == "metadata":
            # Metadata tables might need unique constraints
            pass

        return indexes

    def _generate_sample_data(self, database_name: str, database_spec: dict[str, Any]) -> list[str]:
        """Generate sample data insertion statements.

        Args:
            database_name: Name of the database.
            database_spec: Database specification from YAML.

        Returns:
            List of SQL INSERT statements.
        """
        sql_lines = [
            "-- ============================================================================",
            f"-- SAMPLE DATA FOR {database_name.upper()}",
            "-- ============================================================================",
            "",
        ]

        if database_name == "alphaloop_sys":
            # Sample system metadata
            sql_lines.extend(
                [
                    "-- Insert sample system metadata",
                    "\\c alphaloop_sys;",
                    "INSERT INTO system_attributes (",
                    "    host_name, system_name, node_name, machine, kernel_version,",
                    "    cpu_cores, cpu_cores_logical, ram_total, ssd_total, boot_time",
                    ") VALUES (",
                    "    'alphaloop-node-001',",
                    "    'Linux',",
                    "    'alphaloop-node-001',",
                    "    'x86_64',",
                    "    '5.15.0-generic',",
                    "    8,",
                    "    16,",
                    "    34359738368.0,  -- 32GB",
                    "    1099511627776.0, -- 1TB",
                    "    CURRENT_TIMESTAMP - INTERVAL '1 hour'",
                    ");",
                    "",
                ]
            )

        elif database_name == "alphaloop_market":
            # Sample market metadata
            sql_lines.extend(
                [
                    "-- Insert sample market metadata",
                    "\\c alphaloop_market;",
                    "INSERT INTO tickers_metadata (ticker, base, quote, exchange, active) VALUES",
                    "('BTC/USDT', 'BTC', 'USDT', 'binance', true),",
                    "('ETH/USDT', 'ETH', 'USDT', 'binance', true),",
                    "('ADA/USDT', 'ADA', 'USDT', 'binance', true),",
                    "('DOT/USDT', 'DOT', 'USDT', 'binance', true);",
                    "",
                ]
            )

        return sql_lines

    def generate_database_sql(self, database_name: str, database_spec: dict[str, Any]) -> str:
        """Generate complete SQL for a database.

        Args:
            database_name: Name of the database.
            database_spec: Database specification from YAML.

        Returns:
            Complete SQL for the database.
        """
        sql_lines = [
            "-- ============================================================================",
            f"-- {database_name.upper()} DATABASE",
            "-- ============================================================================",
            f"\\c {database_name};",
            "",
        ]

        # Create tables
        for table_name, table_spec in database_spec["tables"].items():
            sql_lines.append(f"-- {table_spec.get('description', table_name)}")
            sql_lines.append(self._generate_table_sql(table_name, table_spec))
            sql_lines.append("")

            # Add indexes
            indexes = self._generate_indexes(table_name, table_spec)
            for index in indexes:
                sql_lines.append(index)
            sql_lines.append("")

        return "\n".join(sql_lines)

    def generate_complete_sql(self, include_sample_data: bool = True) -> str:
        """Generate complete SQL schema from YAML.

        Args:
            include_sample_data: Whether to include sample data insertion.

        Returns:
            Complete SQL schema as a string.
        """
        schema = self.load_schema()

        sql_lines = [
            "-- AlphaLoop Database Schemas - Generated from YAML",
            f"-- Source: {self.yaml_path}",
            "-- DO NOT EDIT MANUALLY - This is auto-generated",
            "",
            "-- Drop existing databases if they exist",
            "DROP DATABASE IF EXISTS alphaloop_sys;",
            "DROP DATABASE IF EXISTS alphaloop_market;",
            "",
            "-- Create fresh databases",
            "CREATE DATABASE alphaloop_sys;",
            "CREATE DATABASE alphaloop_market;",
            "",
        ]

        # Generate SQL for each database
        for database_name, database_spec in schema["databases"].items():
            sql_lines.append(self.generate_database_sql(database_name, database_spec))
            sql_lines.append("")

            if include_sample_data:
                sql_lines.extend(self._generate_sample_data(database_name, database_spec))

        # Add final commands
        sql_lines.extend(
            [
                "-- Show created tables",
                "\\c alphaloop_sys;",
                "\\dt",
                "",
                "\\c alphaloop_market;",
                "\\dt",
                "",
            ]
        )

        return "\n".join(sql_lines)

    def save_sql_to_file(self, output_path: str, include_sample_data: bool = True) -> None:
        """Generate SQL and save it to a file.

        Args:
            output_path: Path where to save the SQL file.
            include_sample_data: Whether to include sample data insertion.
        """
        sql_content = self.generate_complete_sql(include_sample_data)

        with open(output_path, "w") as file:
            file.write(sql_content)


def create_schema_generator(yaml_path: str | None = None) -> SchemaGenerator:
    """Factory function to create a schema generator.

    Args:
        yaml_path: Path to the YAML schema file. If None, uses default path.

    Returns:
        Configured SchemaGenerator instance.
    """
    return SchemaGenerator(yaml_path)


def generate_sql_from_yaml(yaml_path: str | None = None, output_path: str | None = None) -> str:
    """Convenience function to generate SQL from YAML.

    Args:
        yaml_path: Path to the YAML schema file. If None, uses default path.
        output_path: Path where to save the SQL file. If None, only returns the SQL.

    Returns:
        Generated SQL as a string.
    """
    generator = create_schema_generator(yaml_path)
    sql_content = generator.generate_complete_sql()

    if output_path:
        generator.save_sql_to_file(output_path)

    return sql_content
