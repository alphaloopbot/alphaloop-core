"""Database schema configuration loader."""

from pathlib import Path
from typing import Any

import yaml  # type: ignore
from alphaloop_core.shared.exceptions.validation_exceptions import (
    ValidationError as ConfigurationError,
)


class DatabaseSchemaLoader:
    """Loads and validates database schema configuration from YAML."""

    def __init__(self, config_path: str | None = None) -> None:
        """Initialize the schema loader."""
        if config_path is None:
            # Default to config/database_schema.yaml relative to project root
            project_root = Path(__file__).parent.parent.parent.parent.parent
            config_path = str(project_root / "config" / "database_schema.yaml")

        self.config_path = Path(config_path)
        self._schema: dict[str, Any] | None = None

    def load_schema(self) -> dict[str, Any]:
        """Load the database schema configuration."""
        if self._schema is not None:
            return self._schema

        if not self.config_path.exists():
            raise ConfigurationError(f"Schema configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, encoding="utf-8") as f:
                loaded_schema = yaml.safe_load(f)
                if loaded_schema is None:
                    raise ConfigurationError("Schema configuration file is empty")
                self._schema = loaded_schema
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in schema configuration: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"Failed to load schema configuration: {e}") from e

        self._validate_schema()
        assert self._schema is not None
        return self._schema

    def _validate_schema(self) -> None:
        """Validate the loaded schema configuration."""
        if not isinstance(self._schema, dict):
            raise ConfigurationError("Schema configuration must be a dictionary")

        required_sections = ["databases", "systems", "tasks"]
        for section in required_sections:
            if section not in self._schema:
                raise ConfigurationError(f"Missing required section: {section}")

        # Validate databases
        for db_name, db_config in self._schema["databases"].items():
            if "domain" not in db_config:
                raise ConfigurationError(f"Database {db_name} missing 'domain' field")
            if "tables" not in db_config:
                raise ConfigurationError(f"Database {db_name} missing 'tables' field")

            # Validate tables
            for table_name, table_config in db_config["tables"].items():
                if "type" not in table_config:
                    raise ConfigurationError(f"Table {table_name} missing 'type' field")
                if "columns" not in table_config:
                    raise ConfigurationError(f"Table {table_name} missing 'columns' field")

    def get_database_config(self, database_name: str) -> dict[str, Any]:
        """Get configuration for a specific database."""
        schema = self.load_schema()
        if database_name not in schema["databases"]:
            raise ConfigurationError(f"Database '{database_name}' not found in schema")
        return schema["databases"][database_name]

    def get_table_config(self, database_name: str, table_name: str) -> dict[str, Any]:
        """Get configuration for a specific table."""
        db_config = self.get_database_config(database_name)
        if table_name not in db_config["tables"]:
            raise ConfigurationError(
                f"Table '{table_name}' not found in database '{database_name}'"
            )
        return db_config["tables"][table_name]

    def get_system_config(self, system_name: str) -> dict[str, Any]:
        """Get configuration for a specific system."""
        schema = self.load_schema()
        if system_name not in schema["systems"]:
            raise ConfigurationError(f"System '{system_name}' not found in schema")
        return schema["systems"][system_name]

    def get_tables_for_system(self, system_name: str) -> dict[str, dict[str, Any]]:
        """Get all tables available for a specific system."""
        system_config = self.get_system_config(system_name)

        tables = {}
        for db_name in system_config.get("databases", []):
            db_config = self.get_database_config(db_name)
            for table_name, table_config in db_config["tables"].items():
                # Check if table has policies for this system
                policies = table_config.get("policies", {})
                for policy_name, policy_config in policies.items():
                    if policy_name == system_name or policy_name.startswith(f"{system_name}_"):
                        full_table_name = (
                            f"{table_name}_{policy_config.get('suffix_name', '')}"
                            if policy_config.get("suffix_name")
                            else table_name
                        )
                        tables[full_table_name] = {
                            **table_config,
                            "database": db_name,
                            "policy": policy_name,
                            "policy_config": policy_config,
                        }

        return tables

    def get_tables_by_task(
        self, task_name: str, system_name: str | None = None
    ) -> dict[str, dict[str, Any]]:
        """Get all tables that have a specific task configured."""
        schema = self.load_schema()
        tables = {}

        for db_name, db_config in schema["databases"].items():
            for table_name, table_config in db_config["tables"].items():
                policies = table_config.get("policies", {})
                for policy_name, policy_config in policies.items():
                    # Filter by system if specified
                    if system_name and not (
                        policy_name == system_name or policy_name.startswith(f"{system_name}_")
                    ):
                        continue

                    tasks = policy_config.get("tasks", [])
                    if task_name in tasks:
                        full_table_name = (
                            f"{table_name}_{policy_config.get('suffix_name', '')}"
                            if policy_config.get("suffix_name")
                            else table_name
                        )
                        tables[full_table_name] = {
                            **table_config,
                            "database": db_name,
                            "policy": policy_name,
                            "policy_config": policy_config,
                        }

        return tables

    def get_time_constants(self) -> dict[str, int]:
        """Get time constants from the schema."""
        schema = self.load_schema()
        return schema.get("time_constants", {})


# Global schema loader instance
_schema_loader: DatabaseSchemaLoader | None = None


def get_schema_loader() -> DatabaseSchemaLoader:
    """Get the global schema loader instance."""
    global _schema_loader
    if _schema_loader is None:
        _schema_loader = DatabaseSchemaLoader()
    return _schema_loader


def load_schema() -> dict[str, Any]:
    """Load the database schema configuration."""
    return get_schema_loader().load_schema()
