"""Abstract base class for all domain entities."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from alphaloop_core.shared.types.enums import EntityStatus


class Entity(ABC):
    """Abstract base class for all domain entities."""

    def __init__(
        self,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        status: EntityStatus = EntityStatus.ACTIVE,
    ) -> None:
        """Initialize the entity with common properties."""
        self._id = id or uuid4()
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = updated_at or datetime.now(timezone.utc)
        self._status = status

    @property
    def id(self) -> UUID:
        """Get the entity ID."""
        return self._id

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get the last update timestamp."""
        return self._updated_at

    @property
    def status(self) -> EntityStatus:
        """Get the entity status."""
        return self._status

    def update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self._updated_at = datetime.now(timezone.utc)

    def activate(self) -> None:
        """Activate the entity."""
        self._status = EntityStatus.ACTIVE
        self.update_timestamp()

    def deactivate(self) -> None:
        """Deactivate the entity."""
        self._status = EntityStatus.INACTIVE
        self.update_timestamp()

    def delete(self) -> None:
        """Mark the entity as deleted."""
        self._status = EntityStatus.DELETED
        self.update_timestamp()

    def is_active(self) -> bool:
        """Check if the entity is active."""
        return self._status == EntityStatus.ACTIVE

    def is_deleted(self) -> bool:
        """Check if the entity is deleted."""
        return self._status == EntityStatus.DELETED

    @abstractmethod
    def validate(self) -> bool:
        """Validate the entity state."""
        pass

    def to_dict(self) -> dict[str, Any]:
        """Convert entity to dictionary representation."""
        return {
            "id": str(self._id),
            "created_at": self._created_at.replace(tzinfo=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            "updated_at": self._updated_at.replace(tzinfo=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            "status": self._status.value,
        }

    def __eq__(self, other: Any) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, Entity):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self._id)

    def __repr__(self) -> str:
        """String representation of the entity."""
        return f"{self.__class__.__name__}(id={self._id})"
