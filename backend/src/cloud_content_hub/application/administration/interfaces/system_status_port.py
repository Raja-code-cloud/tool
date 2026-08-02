"""System status port for operational health summaries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol


class SystemHealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"


class DependencyHealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class DependencyStatusRecord:
    """Single dependency health projection."""

    name: str
    status: DependencyHealthStatus


@dataclass(frozen=True, slots=True)
class SystemStatusRecord:
    """Operational system status read model."""

    status: SystemHealthStatus
    version: str
    started_at: datetime
    dependencies: tuple[DependencyStatusRecord, ...]
    maintenance_enabled: bool


class ISystemStatusPort(Protocol):
    """Port for retrieving aggregate system health."""

    async def get_status(self) -> SystemStatusRecord:
        """Return the current operational system status."""
