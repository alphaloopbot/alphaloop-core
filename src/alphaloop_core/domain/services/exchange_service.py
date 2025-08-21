"""Exchange service interface."""

from abc import ABC, abstractmethod

from ..value_objects.exchange_id import ExchangeId


class ExchangeService(ABC):
    """Abstract exchange service interface."""

    @abstractmethod
    async def is_exchange_available(self, exchange_id: ExchangeId) -> bool:
        """Check if an exchange is available."""
        pass

    @abstractmethod
    async def get_available_exchanges(self) -> list[ExchangeId]:
        """Get list of available exchanges."""
        pass

    @abstractmethod
    async def get_exchange_info(self, exchange_id: ExchangeId) -> dict:
        """Get information about an exchange."""
        pass

    @abstractmethod
    async def get_exchange_status(self, exchange_id: ExchangeId) -> str:
        """Get the status of an exchange."""
        pass
