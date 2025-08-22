#!/usr/bin/env python3
"""
Basic test for AlphaLoop Storage package.
"""

import asyncio

from alphaloop_storage import (
    DatabaseConfig,
    DatabaseManager,
    SchemaManager,
)


async def test_database_config():
    """Test database configuration."""
    print("🔧 Testing Database Configuration")
    print("=" * 40)

    # Test basic configuration
    config = DatabaseConfig(
        host="localhost",
        database="test_db",
        username="test_user",
        password="test_pass",
        port=5432,
    )

    print(f"📁 Host: {config.host}")
    print(f"📁 Database: {config.database}")
    print(f"📁 Username: {config.username}")
    print(f"📁 Port: {config.port}")

    # Test URL generation
    sync_url = config.sync_url
    async_url = config.async_url

    print(f"🔗 Sync URL: {sync_url}")
    print(f"🔗 Async URL: {async_url}")

    assert "postgresql://" in sync_url
    assert "postgresql+asyncpg://" in async_url
    assert "test_db" in sync_url
    assert "test_db" in async_url

    print("✅ Database configuration test passed\n")


async def test_schema_manager():
    """Test schema manager functionality."""
    print("📋 Testing Schema Manager")
    print("=" * 40)

    from alphaloop_storage import ColumnDefinition, TableDefinition

    # Create a test table definition
    columns = [
        ColumnDefinition(name="name", type="VARCHAR(255)", nullable=False),
        ColumnDefinition(name="age", type="INTEGER", nullable=True),
        ColumnDefinition(name="email", type="VARCHAR(255)", unique=True),
    ]

    table_def = TableDefinition(name="test_users", columns=columns, auto_id=True)

    # Test schema manager
    schema_manager = SchemaManager()
    schema_manager.register_table(table_def)

    print(f"📄 Registered table: {table_def.name}")
    print(f"📄 Columns: {[col.name for col in table_def.columns]}")

    # Test table retrieval
    retrieved_table = schema_manager.get_table("test_users")
    assert retrieved_table is not None
    assert retrieved_table.name == "test_users"

    # Test schema export
    schema_export = schema_manager.export_schema()
    print(f"📄 Exported schema: {list(schema_export['tables'].keys())}")

    # Test SQL DDL generation
    ddl = schema_manager.create_sql_ddl("test_users")
    print(f"🔧 Generated DDL: {ddl[:100]}...")

    assert "CREATE TABLE test_users" in ddl
    assert "id SERIAL PRIMARY KEY" in ddl
    assert "name VARCHAR(255) NOT NULL" in ddl

    print("✅ Schema manager test passed\n")


async def test_query_builder():
    """Test query builder functionality."""
    print("🔍 Testing Query Builder")
    print("=" * 40)

    from alphaloop_storage import QueryBuilder

    # Test basic query building
    builder = QueryBuilder("test_table")

    query = (
        builder.select(["id", "name", "email"])
        .where_equals("status", "active")
        .where_between("age", 18, 65)
        .order_by("name", "ASC")
        .limit(10)
        .build()
    )

    print(f"🔍 Built query: {query}")

    assert "SELECT id, name, email" in query
    assert "FROM test_table" in query
    assert "WHERE status = 'active'" in query
    assert "BETWEEN 18 AND 65" in query
    assert "ORDER BY name ASC" in query
    assert "LIMIT 10" in query

    # Test static query creation
    static_query = QueryBuilder.create_select_query(
        table_name="users",
        columns=["id", "name"],
        where_conditions={"status": "active", "age": [18, 25, 30]},
        order_by=["name ASC", "created_at DESC"],
        limit=5,
    )

    print(f"🔍 Static query: {static_query}")

    assert "SELECT id, name" in static_query
    assert "FROM users" in static_query
    assert "WHERE status = 'active'" in static_query
    assert "age IN (18, 25, 30)" in static_query

    print("✅ Query builder test passed\n")


async def test_database_manager():
    """Test database manager (without actual connection)."""
    print("🗄️ Testing Database Manager")
    print("=" * 40)

    # Create a test configuration
    config = DatabaseConfig(
        host="localhost", database="test_db", username="test_user", password="test_pass"
    )

    # Create database manager
    db_manager = DatabaseManager(config)

    print(f"📁 Database: {db_manager.config.database}")
    print(f"📁 Host: {db_manager.config.host}")

    # Test that engines are created lazily
    assert db_manager._sync_engine is None
    assert db_manager._async_engine is None

    # Note: We don't test actual connections here since we don't have a database
    # In a real test environment, you would use a test database or mock

    print("✅ Database manager test passed\n")


async def main():
    """Run all basic tests."""
    print("🚀 AlphaLoop Storage Package - Basic Tests")
    print("=" * 60)
    print()

    try:
        await test_database_config()
        await test_schema_manager()
        await test_query_builder()
        await test_database_manager()

        print("🎉 All basic tests completed successfully!")
        print("✅ AlphaLoop Storage package is working correctly")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
