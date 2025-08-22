"""Abstract base interface for all repositories."""

from abc import ABC, abstractmethod
from typing import Any, TypeVar
from uuid import UUID

from ..entities.base import Entity

T = TypeVar("T", bound=Entity)


class Repository[T](ABC):
    """Abstract base interface for all repositories with common CRUD operations."""

    @abstractmethod
    async def add(self, entity: T) -> T:
        """Add a new entity to the repository."""
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> T | None:
        """Get an entity by its ID."""
        pass

    @abstractmethod
    async def get_all(self, limit: int | None = None, offset: int | None = None) -> list[T]:
        """Get all entities with optional pagination."""
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an existing entity."""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete an entity by its ID."""
        pass

    @abstractmethod
    async def exists(self, id: UUID) -> bool:
        """Check if an entity exists by its ID."""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Get the total count of entities."""
        pass

    @abstractmethod
    async def find_by_criteria(self, criteria: dict[str, Any]) -> list[T]:
        """Find entities by criteria."""
        pass

    @abstractmethod
    async def find_one_by_criteria(self, criteria: dict[str, Any]) -> T | None:
        """Find a single entity by criteria."""
        pass


class ReadOnlyRepository[T](ABC):
    """Abstract base interface for read-only repositories."""

    @abstractmethod
    async def get_by_id(self, id: UUID) -> T | None:
        """Get an entity by its ID."""
        pass

    @abstractmethod
    async def get_all(self, limit: int | None = None, offset: int | None = None) -> list[T]:
        """Get all entities with optional pagination."""
        pass

    @abstractmethod
    async def exists(self, id: UUID) -> bool:
        """Check if an entity exists by its ID."""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Get the total count of entities."""
        pass

    @abstractmethod
    async def find_by_criteria(self, criteria: dict[str, Any]) -> list[T]:
        """Find entities by criteria."""
        pass

    @abstractmethod
    async def find_one_by_criteria(self, criteria: dict[str, Any]) -> T | None:
        """Find a single entity by criteria."""
        pass
