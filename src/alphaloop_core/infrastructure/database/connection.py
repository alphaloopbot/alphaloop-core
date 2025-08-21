"""Database connection management and pooling."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ...shared.exceptions.infrastructure_exceptions import DatabaseConnectionError
from ...shared.utils.config import get_database_url


class DatabaseConnectionManager:
    """Manages database connections and connection pooling."""

    def __init__(
        self,
        database_url: str | None = None,
        pool_size: int = 20,
        max_overflow: int = 30,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False,
    ) -> None:
        """Initialize the database connection manager."""
        self._database_url = database_url or get_database_url()
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._pool_timeout = pool_timeout
        self._pool_recycle = pool_recycle
        self._echo = echo

        self._engine: object | None = None
        self._session_factory: async_sessionmaker | None = None
        self._pool: asyncpg.Pool | None = None
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize the database connection pool."""
        async with self._lock:
            if self._engine is not None:
                return

            try:
                # Create SQLAlchemy async engine
                self._engine = create_async_engine(
                    self._database_url,
                    pool_size=self._pool_size,
                    max_overflow=self._max_overflow,
                    pool_timeout=self._pool_timeout,
                    pool_recycle=self._pool_recycle,
                    echo=self._echo,
                    pool_pre_ping=True,
                )

                # Create session factory
                self._session_factory = async_sessionmaker(
                    bind=self._engine,
                    class_=AsyncSession,
                    expire_on_commit=False,
                )

                # Test the connection
                async with self._engine.begin() as conn:
                    await conn.execute("SELECT 1")

            except Exception as e:
                raise DatabaseConnectionError(
                    f"Failed to initialize database connection: {str(e)}"
                ) from e

    async def get_session(self) -> AsyncSession:
        """Get a database session."""
        if self._session_factory is None:
            await self.initialize()

        if self._session_factory is None:
            raise DatabaseConnectionError("Database session factory not initialized")

        return self._session_factory()

    @asynccontextmanager
    async def get_session_context(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session with automatic cleanup."""
        session = await self.get_session()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def get_raw_connection(self) -> asyncpg.Connection:
        """Get a raw asyncpg connection for direct SQL operations."""
        if self._pool is None:
            await self._initialize_raw_pool()

        if self._pool is None:
            raise DatabaseConnectionError("Database pool not initialized")

        return await self._pool.acquire()

    async def _initialize_raw_pool(self) -> None:
        """Initialize the raw connection pool."""
        async with self._lock:
            if self._pool is not None:
                return

            try:
                # Parse database URL for asyncpg
                db_url = self._database_url.replace("postgresql+asyncpg://", "postgresql://")

                self._pool = await asyncpg.create_pool(
                    db_url,
                    min_size=5,
                    max_size=self._pool_size,
                    command_timeout=self._pool_timeout,
                )

            except Exception as e:
                raise DatabaseConnectionError(
                    f"Failed to initialize raw connection pool: {str(e)}"
                ) from e

    @asynccontextmanager
    async def get_raw_connection_context(
        self,
    ) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get a raw connection with automatic cleanup."""
        conn = await self.get_raw_connection()
        try:
            yield conn
        finally:
            await self._pool.release(conn)

    async def close(self) -> None:
        """Close all database connections."""
        async with self._lock:
            if self._engine is not None:
                await self._engine.dispose()
                self._engine = None
                self._session_factory = None

            if self._pool is not None:
                await self._pool.close()
                self._pool = None

    async def health_check(self) -> bool:
        """Perform a health check on the database connection."""
        try:
            async with self.get_session_context() as session:
                await session.execute("SELECT 1")
            return True
        except Exception:
            return False

    async def get_connection_info(self) -> dict:
        """Get information about the database connection."""
        return {
            "database_url": (
                self._database_url.replace("://", "://***:***@")
                if "://" in self._database_url
                else "***"
            ),
            "pool_size": self._pool_size,
            "max_overflow": self._max_overflow,
            "pool_timeout": self._pool_timeout,
            "pool_recycle": self._pool_recycle,
            "echo": self._echo,
            "engine_initialized": self._engine is not None,
            "session_factory_initialized": self._session_factory is not None,
            "raw_pool_initialized": self._pool is not None,
        }

    async def __aenter__(self) -> "DatabaseConnectionManager":
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()


# Global database connection manager instance
_db_manager: DatabaseConnectionManager | None = None


async def get_database_manager() -> DatabaseConnectionManager:
    """Get the global database connection manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseConnectionManager()
        await _db_manager.initialize()
    return _db_manager


async def close_database_manager() -> None:
    """Close the global database connection manager."""
    global _db_manager
    if _db_manager is not None:
        await _db_manager.close()
        _db_manager = None
