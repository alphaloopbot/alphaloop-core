"""
Database connection management for AlphaLoop Storage.

This module provides comprehensive database connection management for the AlphaLoop
Storage system, supporting both synchronous and asynchronous database operations
with connection pooling, configuration management, and error handling.

The module includes configuration management, connection pooling, session
management, and utilities for database operations with proper resource cleanup.

Key Features:
- Synchronous and asynchronous database support
- Connection pooling and management
- Configuration from environment variables
- Session management with context managers
- Error handling and validation
- SSL/TLS support
- Connection health monitoring
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from infrastructure.alphaloop_storage.exceptions import DatabaseConnectionError, DatabaseQueryError
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


@dataclass
class DatabaseConfig:
    """
    Configuration for database connections.

    This class encapsulates all configuration parameters needed for database
    connections, including connection details, pooling settings, and security
    parameters. It provides validation and environment variable loading
    capabilities.

    The configuration supports both development and production environments
    with sensible defaults and comprehensive validation.

    Key Features:
    - Connection parameter management
    - Environment variable loading
    - Configuration validation
    - SSL/TLS support
    - Connection pooling configuration
    - Timeout settings

    Usage:
        config = DatabaseConfig.from_env(prefix="DB_")
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="myapp"
        )
    """

    host: str
    port: int = 5432
    username: str = "postgres"
    password: str = ""
    database: str = "alphaloop"
    application_name: str = "alphaloop-storage"
    ssl_mode: str = "prefer"
    max_connections: int = 20
    min_connections: int = 5
    connection_timeout: int = 30
    command_timeout: int = 60

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.host:
            raise ValueError("Database host is required")
        if not self.database:
            raise ValueError("Database name is required")
        if self.port <= 0 or self.port > 65535:
            raise ValueError("Invalid port number")

    @property
    def sync_url(self) -> str:
        """Get synchronous database URL."""
        return (
            f"postgresql://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
            f"?application_name={self.application_name}"
            f"&sslmode={self.ssl_mode}"
        )

    @property
    def async_url(self) -> str:
        """Get asynchronous database URL."""
        return (
            f"postgresql+asyncpg://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
        )

    @classmethod
    def from_env(cls, prefix: str = "DB_") -> "DatabaseConfig":
        """Create configuration from environment variables."""
        import os

        return cls(
            host=os.getenv(f"{prefix}HOST", "localhost"),
            port=int(os.getenv(f"{prefix}PORT", "5432")),
            username=os.getenv(f"{prefix}USER", "postgres"),
            password=os.getenv(f"{prefix}PASSWORD", ""),
            database=os.getenv(f"{prefix}NAME", "alphaloop"),
            application_name=os.getenv(f"{prefix}APP_NAME", "alphaloop-storage"),
            ssl_mode=os.getenv(f"{prefix}SSL_MODE", "prefer"),
            max_connections=int(os.getenv(f"{prefix}MAX_CONNECTIONS", "20")),
            min_connections=int(os.getenv(f"{prefix}MIN_CONNECTIONS", "5")),
            connection_timeout=int(os.getenv(f"{prefix}CONNECTION_TIMEOUT", "30")),
            command_timeout=int(os.getenv(f"{prefix}COMMAND_TIMEOUT", "60")),
        )


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self, config: DatabaseConfig) -> None:
        """Initialize database manager."""
        self.config = config
        self._sync_engine: Engine | None = None
        self._async_engine: AsyncEngine | None = None
        self._sync_session_factory: sessionmaker | None = None
        self._async_session_factory: sessionmaker | None = None

    @property
    def sync_engine(self) -> Engine:
        """Get synchronous database engine."""
        if self._sync_engine is None:
            self._sync_engine = create_engine(
                self.config.sync_url,
                pool_size=self.config.max_connections,
                max_overflow=0,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False,
            )
        return self._sync_engine

    @property
    def async_engine(self) -> AsyncEngine:
        """Get asynchronous database engine."""
        if self._async_engine is None:
            self._async_engine = create_async_engine(
                self.config.async_url,
                pool_size=self.config.max_connections,
                max_overflow=0,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False,
            )
        return self._async_engine

    @property
    def sync_session_factory(self) -> sessionmaker:
        """Get synchronous session factory."""
        if self._sync_session_factory is None:
            self._sync_session_factory = sessionmaker(
                bind=self.sync_engine,
                autocommit=False,
                autoflush=False,
            )
        return self._sync_session_factory

    @property
    def async_session_factory(self) -> sessionmaker:
        """Get asynchronous session factory."""
        if self._async_session_factory is None:
            self._async_session_factory = sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                autocommit=False,
                autoflush=False,
            )
        return self._async_session_factory

    def create_sync_session(self) -> Any:
        """Create a synchronous database session."""
        return self.sync_session_factory()

    def create_async_session(self) -> AsyncSession:
        """Create an asynchronous database session."""
        return self.async_session_factory()

    @asynccontextmanager
    async def async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide an asynchronous transactional scope."""
        session = self.create_async_session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    def sync_session_scope(self):
        """Provide a synchronous transactional scope."""
        session = self.create_sync_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    async def test_connection(self) -> bool:
        """Test database connection."""
        try:
            async with self.async_session() as session:
                result = await session.execute(text("SELECT 1"))
                result.fetchone()
                return True
        except Exception as e:
            raise DatabaseConnectionError(f"Database connection test failed: {e}") from e

    async def get_database_info(self) -> dict[str, Any]:
        """Get database information."""
        try:
            async with self.async_session() as session:
                # Get PostgreSQL version
                version_result = await session.execute(text("SELECT version()"))
                version = version_result.fetchone()[0]

                # Get database size
                size_result = await session.execute(
                    text("SELECT pg_size_pretty(pg_database_size(current_database()))")
                )
                size = size_result.fetchone()[0]

                # Get connection count
                conn_result = await session.execute(
                    text("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()")
                )
                connections = conn_result.fetchone()[0]

                return {
                    "version": version,
                    "database": self.config.database,
                    "size": size,
                    "active_connections": connections,
                    "host": self.config.host,
                    "port": self.config.port,
                }
        except Exception as e:
            raise DatabaseQueryError(f"Failed to get database info: {e}") from e

    async def close(self) -> None:
        """Close database connections."""
        if self._async_engine:
            await self._async_engine.dispose()
        if self._sync_engine:
            self._sync_engine.dispose()


# Convenience function for creating database manager
def create_database_manager(
    host: str,
    database: str,
    username: str = "postgres",
    password: str = "",
    port: int = 5432,
    **kwargs: Any,
) -> DatabaseManager:
    """Create a database manager with the given configuration."""
    config = DatabaseConfig(
        host=host,
        database=database,
        username=username,
        password=password,
        port=port,
        **kwargs,
    )
    return DatabaseManager(config)
