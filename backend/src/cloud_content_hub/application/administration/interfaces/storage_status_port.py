"""Storage status port for administrative storage health summaries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class StorageHealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class StorageStatusRecord:
    """Storage subsystem health projection."""

    status: StorageHealthStatus
    provider_code: str
    checked_at: datetime
    container_count: int
    message: str | None = None


class IStorageStatusPort(Protocol):
    """Port for retrieving storage health summaries."""

    async def get_status(self, *, workspace_id: UUID | None) -> StorageStatusRecord:
        """Return the current storage subsystem status."""
