"""System metadata entity for hardware and configuration information."""

from datetime import datetime
from typing import Any
from uuid import UUID

from alphaloop_core.domain.entities.base import Entity


class SystemMetadata(Entity):
    """System metadata entity representing hardware and configuration information."""

    def __init__(
        self,
        kernel_version: str,
        system_name: str,
        node_name: str,
        host_name: str,
        machine: str,
        boot_time: datetime,
        app_start_time: datetime,
        cpu_cores: int,
        cpu_cores_logical: int,
        ram_total: float,
        swap_total: float,
        ssd_total: float,
        entity_id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize the system metadata entity."""
        super().__init__(entity_id, created_at, updated_at)

        self._kernel_version = kernel_version
        self._system_name = system_name
        self._node_name = node_name
        self._host_name = host_name
        self._machine = machine
        self._boot_time = boot_time
        self._app_start_time = app_start_time
        self._cpu_cores = cpu_cores
        self._cpu_cores_logical = cpu_cores_logical
        self._ram_total = ram_total
        self._swap_total = swap_total
        self._ssd_total = ssd_total

    @property
    def kernel_version(self) -> str:
        """Get the kernel version."""
        return self._kernel_version

    @property
    def system_name(self) -> str:
        """Get the system name."""
        return self._system_name

    @property
    def node_name(self) -> str:
        """Get the node name."""
        return self._node_name

    @property
    def host_name(self) -> str:
        """Get the host name."""
        return self._host_name

    @property
    def machine(self) -> str:
        """Get the machine identifier."""
        return self._machine

    @property
    def boot_time(self) -> datetime:
        """Get the system boot time."""
        return self._boot_time

    @property
    def app_start_time(self) -> datetime:
        """Get the application start time."""
        return self._app_start_time

    @property
    def cpu_cores(self) -> int:
        """Get the number of physical CPU cores."""
        return self._cpu_cores

    @property
    def cpu_cores_logical(self) -> int:
        """Get the number of logical CPU cores."""
        return self._cpu_cores_logical

    @property
    def ram_total(self) -> float:
        """Get the total RAM in bytes."""
        return self._ram_total

    @property
    def swap_total(self) -> float:
        """Get the total swap space in bytes."""
        return self._swap_total

    @property
    def ssd_total(self) -> float:
        """Get the total SSD space in bytes."""
        return self._ssd_total

    def to_dict(self) -> dict[str, Any]:
        """Convert the entity to a dictionary."""
        base_dict = super().to_dict()
        return {
            **base_dict,
            "kernel_version": self._kernel_version,
            "system_name": self._system_name,
            "node_name": self._node_name,
            "host_name": self._host_name,
            "machine": self._machine,
            "boot_time": self._boot_time.isoformat(),
            "app_start_time": self._app_start_time.isoformat(),
            "cpu_cores": self._cpu_cores,
            "cpu_cores_logical": self._cpu_cores_logical,
            "ram_total": self._ram_total,
            "swap_total": self._swap_total,
            "ssd_total": self._ssd_total,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SystemMetadata":
        """Create a SystemMetadata entity from a dictionary."""
        return cls(
            kernel_version=data["kernel_version"],
            system_name=data["system_name"],
            node_name=data["node_name"],
            host_name=data["host_name"],
            machine=data["machine"],
            boot_time=datetime.fromisoformat(data["boot_time"]),
            app_start_time=datetime.fromisoformat(data["app_start_time"]),
            cpu_cores=data["cpu_cores"],
            cpu_cores_logical=data["cpu_cores_logical"],
            ram_total=data["ram_total"],
            swap_total=data["swap_total"],
            ssd_total=data["ssd_total"],
            entity_id=data.get("id"),
            created_at=(
                datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
            ),
            updated_at=(
                datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
            ),
        )
