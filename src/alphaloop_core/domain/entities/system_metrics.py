"""System metrics entity for real-time monitoring data."""

from datetime import datetime
from typing import Any
from uuid import UUID

from alphaloop_core.domain.entities.base import Entity


class SystemMetrics(Entity):
    """System metrics entity representing real-time monitoring data."""

    def __init__(
        self,
        metadata_id: int,
        timestamp_id: int,
        cpu_usage: float,
        cores_usage: dict[str, float],
        core_usage_max: float,
        core_usage_min: float,
        ram_usage: float,
        ssd_usage: float,
        cpu_temperature: float | None = None,
        cpu_speed: int | None = None,
        swap_usage: float | None = None,
        ip_address: str | None = None,
        ip_renewed: bool | None = None,
        entity_id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize the system metrics entity."""
        super().__init__(entity_id, created_at, updated_at)

        self._metadata_id = int(metadata_id)
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

    def validate(self) -> bool:
        """Basic validation for metric ranges and presence."""
        try:
            # Percentages must be within [0, 100]
            for v in (self._cpu_usage, self._core_usage_max, self._core_usage_min, self._ram_usage):
                if not (0.0 <= v <= 100.0):
                    return False
            # Per-core usages must also be [0, 100]
            if any(not (0.0 <= val <= 100.0) for val in self._cores_usage.values()):
                return False
            # Logical invariant: min must not exceed max
            if self._core_usage_min > self._core_usage_max:
                return False
        except Exception:
            return False
        return True

    @property
    def metadata_id(self) -> int:
        """Get the metadata ID reference."""
        return self._metadata_id

    @property
    def timestamp_id(self) -> int:
        """Get the timestamp ID."""
        return self._timestamp_id

    @property
    def cpu_temperature(self) -> float | None:
        """Get the CPU temperature in Celsius."""
        return self._cpu_temperature

    @property
    def cpu_speed(self) -> int | None:
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
    def swap_usage(self) -> float | None:
        """Get the swap usage percentage."""
        return self._swap_usage

    @property
    def ssd_usage(self) -> float:
        """Get the SSD usage percentage."""
        return self._ssd_usage

    @property
    def ip_address(self) -> str | None:
        """Get the current IP address."""
        return self._ip_address

    @property
    def ip_renewed(self) -> bool | None:
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
            metadata_id=int(data["metadata_id"]),
            timestamp_id=data["timestamp_id"],
            cpu_temperature=data.get("cpu_temperature"),
            cpu_speed=data.get("cpu_speed"),
            cpu_usage=data["cpu_usage"],
            cores_usage=data["cores_usage"],
            core_usage_max=data["core_usage_max"],
            core_usage_min=data["core_usage_min"],
            ram_usage=data["ram_usage"],
            swap_usage=data.get("swap_usage"),
            ssd_usage=data["ssd_usage"],
            ip_address=data.get("ip_address"),
            ip_renewed=data.get("ip_renewed"),
            entity_id=UUID(data["id"]) if data.get("id") else None,
            created_at=(
                datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
            ),
            updated_at=(
                datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
            ),
        )
