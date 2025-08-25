"""Service factory for AlphaLoop Core using official infrastructure packages."""

from typing import Any

from infrastructure.alphaloop_cache import CacheManager, PubSubManager
from infrastructure.alphaloop_heartbeat import HeartbeatChecker, HeartbeatGenerator
from infrastructure.alphaloop_logging import AlphaLoopLogger
from infrastructure.alphaloop_security import (
    ConnectionAuthenticator,
    DataEncryptor,
    SecureURLComposer,
)
from infrastructure.alphaloop_storage import DatabaseManager, TableHandler

from .package_config import (
    get_cache_config,
    get_heartbeat_config,
    get_logging_config,
    get_security_config,
    get_storage_config,
)


class ServiceFactory:
    """Factory for creating services using official AlphaLoop infrastructure packages."""

    def __init__(self) -> None:
        """Initialize the service factory."""
        self._cache_manager: CacheManager | None = None
        self._database_manager: DatabaseManager | None = None
        self._logger: AlphaLoopLogger | None = None
        self._heartbeat_generator: HeartbeatGenerator | None = None
        self._heartbeat_checker: HeartbeatChecker | None = None

    async def get_cache_manager(self) -> CacheManager:
        """Get or create cache manager."""
        if self._cache_manager is None:
            config = get_cache_config()
            self._cache_manager = CacheManager(config)
        return self._cache_manager

    async def get_database_manager(self) -> DatabaseManager:
        """Get or create database manager."""
        if self._database_manager is None:
            config = get_storage_config()
            self._database_manager = DatabaseManager(config)
        return self._database_manager

    async def get_logger(self) -> AlphaLoopLogger:
        """Get or create logger."""
        if self._logger is None:
            config = get_logging_config()
            self._logger = AlphaLoopLogger(config)
        return self._logger

    async def get_heartbeat_generator(
        self, service_name: str = "alphaloop-core"
    ) -> HeartbeatGenerator:
        """Get or create heartbeat generator."""
        if self._heartbeat_generator is None:
            config = get_heartbeat_config()
            self._heartbeat_generator = HeartbeatGenerator(service_name, config)
        return self._heartbeat_generator

    async def get_heartbeat_checker(self) -> HeartbeatChecker:
        """Get or create heartbeat checker."""
        if self._heartbeat_checker is None:
            config = get_heartbeat_config()
            self._heartbeat_checker = HeartbeatChecker(config)
        return self._heartbeat_checker

    async def get_price_cache(self) -> Any:
        """Get or create price cache service."""
        from alphaloop_core.services.cache import PriceCacheService

        cache_manager = await self.get_cache_manager()
        return PriceCacheService(cache_manager)

    async def get_pubsub_manager(self) -> PubSubManager:
        """Get or create pub/sub manager."""
        cache_manager = await self.get_cache_manager()
        return PubSubManager(cache_manager)

    async def get_table_handler(self, table_name: str) -> TableHandler:
        """Get or create table handler."""
        database_manager = await self.get_database_manager()
        return TableHandler(table_name, database_manager)

    def get_authenticator(self) -> ConnectionAuthenticator:
        """Get connection authenticator."""
        config = get_security_config()
        return ConnectionAuthenticator(
            passphrase=config["secret_key"],
            period_size=config["time_window"],
            num_sequential_hashes=2,
        )

    def get_encryptor(self) -> DataEncryptor:
        """Get data encryptor."""
        config = get_security_config()
        return DataEncryptor(passphrase=config["secret_key"], period_size=config["time_window"])

    def get_secure_url_composer(
        self,
        target_ip: str = "localhost",
        target_port: int = 8000,
        endpoint: str = "/api",
    ) -> SecureURLComposer:
        """Get secure URL composer."""
        config = get_security_config()
        return SecureURLComposer(
            target_ip=target_ip,
            target_port=target_port,
            endpoint=endpoint,
            passphrase=config["secret_key"],
            period_size=config["time_window"],
        )

    async def close_all(self) -> None:
        """Close all services."""
        if self._cache_manager:
            await self._cache_manager.close()
        if self._database_manager:
            await self._database_manager.close()
        if self._logger:
            await self._logger.close()


# Global service factory instance
service_factory = ServiceFactory()
