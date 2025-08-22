"""System metrics entity for real-time monitoring data."""

from datetime import datetime
from typing import Any
from uuid import UUID

from alphaloop_core.domain.entities.base import Entity


class SystemMetrics(Entity):
    """System metrics entity representing real-time monitoring data."""

    def __init__(
        self,
        metadata_id: str,
        timestamp_id: int,
        cpu_temperature: float,
        cpu_speed: int,
        cpu_usage: float,
        cores_usage: dict[str, float],
        core_usage_max: float,
        core_usage_min: float,
        ram_usage: float,
        swap_usage: float,
        ssd_usage: float,
        ip_address: str,
        ip_renewed: bool,
        entity_id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize the system metrics entity."""
        super().__init__(entity_id, created_at, updated_at)

        self._metadata_id = metadata_id
        self._timestamp_id = timestamp_id
        self._cpu_temperature = cpu_temperature
        self._cpu_speed = cpu_speed
        self._cpu_usage = cpu_usage
        self._cores_usage = cores_usage
        self._core_usage_max = core_usage_max
        self._core_usage_min = core_usage_min
        self._ram_usage = ram_usage
        self._swap_usage = swap_usage
        self._ssd_usage = ssd_usage
        self._ip_address = ip_address
        self._ip_renewed = ip_renewed

    @property
    def metadata_id(self) -> str:
        """Get the metadata ID reference."""
        return self._metadata_id

    @property
    def timestamp_id(self) -> int:
        """Get the timestamp ID."""
        return self._timestamp_id

    @property
    def cpu_temperature(self) -> float:
        """Get the CPU temperature in Celsius."""
        return self._cpu_temperature

    @property
    def cpu_speed(self) -> int:
        """Get the CPU speed in MHz."""
        return self._cpu_speed

    @property
    def cpu_usage(self) -> float:
        """Get the overall CPU usage percentage."""
        return self._cpu_usage

    @property
    def cores_usage(self) -> dict[str, float]:
        """Get the usage percentage for each CPU core."""
        return self._cores_usage.copy()  # Return copy to prevent mutation

    @property
    def core_usage_max(self) -> float:
        """Get the maximum CPU core usage percentage."""
        return self._core_usage_max

    @property
    def core_usage_min(self) -> float:
        """Get the minimum CPU core usage percentage."""
        return self._core_usage_min

    @property
    def ram_usage(self) -> float:
        """Get the RAM usage percentage."""
        return self._ram_usage

    @property
    def swap_usage(self) -> float:
        """Get the swap usage percentage."""
        return self._swap_usage

    @property
    def ssd_usage(self) -> float:
        """Get the SSD usage percentage."""
        return self._ssd_usage

    @property
    def ip_address(self) -> str:
        """Get the current IP address."""
        return self._ip_address

    @property
    def ip_renewed(self) -> bool:
        """Check if the IP address was recently renewed."""
        return self._ip_renewed

    def to_dict(self) -> dict[str, Any]:
        """Convert the entity to a dictionary."""
        base_dict = super().to_dict()
        return {
            **base_dict,
            "metadata_id": self._metadata_id,
            "timestamp_id": self._timestamp_id,
            "cpu_temperature": self._cpu_temperature,
            "cpu_speed": self._cpu_speed,
            "cpu_usage": self._cpu_usage,
            "cores_usage": self._cores_usage,
            "core_usage_max": self._core_usage_max,
            "core_usage_min": self._core_usage_min,
            "ram_usage": self._ram_usage,
            "swap_usage": self._swap_usage,
            "ssd_usage": self._ssd_usage,
            "ip_address": self._ip_address,
            "ip_renewed": self._ip_renewed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SystemMetrics":
        """Create a SystemMetrics entity from a dictionary."""
        return cls(
            metadata_id=data["metadata_id"],
            timestamp_id=data["timestamp_id"],
            cpu_temperature=data["cpu_temperature"],
            cpu_speed=data["cpu_speed"],
            cpu_usage=data["cpu_usage"],
            cores_usage=data["cores_usage"],
            core_usage_max=data["core_usage_max"],
            core_usage_min=data["core_usage_min"],
            ram_usage=data["ram_usage"],
            swap_usage=data["swap_usage"],
            ssd_usage=data["ssd_usage"],
            ip_address=data["ip_address"],
            ip_renewed=data["ip_renewed"],
            entity_id=UUID(data["id"]) if data.get("id") else None,
            created_at=(
                datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
            ),
            updated_at=(
                datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
            ),
        )
