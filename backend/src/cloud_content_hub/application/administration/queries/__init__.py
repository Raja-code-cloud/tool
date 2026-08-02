"""Administration query definitions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from cloud_content_hub.application.administration.interfaces.administration_repository import (
    AuditOutcome,
    UserStatus,
    WorkspaceStatus,
)
from cloud_content_hub.application.administration.interfaces.provider_health_port import (
    ProviderOperationalStatus,
    ProviderType,
)
from cloud_content_hub.application.administration.interfaces.queue_status_port import AdminQueueName


@dataclass(frozen=True, slots=True)
class GetSystemStatusQuery:
    """Query to retrieve operational system status."""


@dataclass(frozen=True, slots=True)
class GetProviderHealthQuery:
    """Query to retrieve provider health summaries."""

    workspace_id: UUID | None = None
    provider_types: frozenset[ProviderType] = frozenset()
    statuses: frozenset[ProviderOperationalStatus] = frozenset()


@dataclass(frozen=True, slots=True)
class GetQueueStatusQuery:
    """Query to retrieve aggregate queue summaries."""

    workspace_id: UUID | None = None
    queue_names: frozenset[AdminQueueName] = frozenset()


@dataclass(frozen=True, slots=True)
class GetStorageStatusQuery:
    """Query to retrieve storage subsystem status."""

    workspace_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class GetIdentityProvidersQuery:
    """Query to retrieve identity provider status."""

    workspace_id: UUID | None = None
    statuses: frozenset[ProviderOperationalStatus] = frozenset()


@dataclass(frozen=True, slots=True)
class GetAIProvidersQuery:
    """Query to retrieve AI provider status."""

    workspace_id: UUID | None = None
    statuses: frozenset[ProviderOperationalStatus] = frozenset()


@dataclass(frozen=True, slots=True)
class ListUsersQuery:
    """Query to list users within an administrative scope."""

    workspace_id: UUID | None = None
    query: str | None = None
    statuses: frozenset[UserStatus] = frozenset()
    cursor: str | None = None
    limit: int = 25
    sort: str = "-updated_at"


@dataclass(frozen=True, slots=True)
class ListWorkspacesQuery:
    """Query to list workspaces within an administrative scope."""

    organization_id: UUID | None = None
    workspace_id: UUID | None = None
    query: str | None = None
    statuses: frozenset[WorkspaceStatus] = frozenset()
    cursor: str | None = None
    limit: int = 25
    sort: str = "-updated_at"


@dataclass(frozen=True, slots=True)
class GetAuditSummaryQuery:
    """Query to retrieve aggregated audit evidence."""

    workspace_id: UUID | None = None
    organization_id: UUID | None = None
    actions: frozenset[str] = frozenset()
    outcomes: frozenset[AuditOutcome] = frozenset()
    occurred_after: datetime | None = None
    occurred_before: datetime | None = None
    limit: int = 25


@dataclass(frozen=True, slots=True)
class GetFeatureFlagsQuery:
    """Query to retrieve read-only feature flags."""

    workspace_id: UUID | None = None
