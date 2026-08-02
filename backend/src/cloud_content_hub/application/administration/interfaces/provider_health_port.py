"""Provider health port for AI, social, storage, notification, and identity providers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class ProviderType(StrEnum):
    AI = "ai"
    SOCIAL = "social"
    STORAGE = "storage"
    NOTIFICATION = "notification"
    IDENTITY = "identity"


class ProviderOperationalStatus(StrEnum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    DEGRADED = "degraded"


@dataclass(frozen=True, slots=True)
class ProviderHealthRecord:
    """Normalized provider health projection."""

    provider_type: ProviderType
    code: str
    name: str
    status: ProviderOperationalStatus
    checked_at: datetime
    message: str | None = None


@dataclass(frozen=True, slots=True)
class ProviderHealthCriteria:
    """Structured provider health query criteria."""

    workspace_id: UUID | None
    provider_types: frozenset[ProviderType] = frozenset()
    statuses: frozenset[ProviderOperationalStatus] = frozenset()


class IProviderHealthPort(Protocol):
    """Port for querying and refreshing provider health."""

    async def list_providers(
        self, criteria: ProviderHealthCriteria
    ) -> tuple[ProviderHealthRecord, ...]:
        """Return normalized provider health summaries."""

    async def refresh_health(
        self,
        *,
        workspace_id: UUID | None,
        provider_types: frozenset[ProviderType],
        refreshed_by: UUID,
    ) -> tuple[ProviderHealthRecord, ...]:
        """Run health checks and return updated provider summaries."""
