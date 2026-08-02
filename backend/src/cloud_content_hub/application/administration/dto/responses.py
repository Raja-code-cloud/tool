"""Administration response DTOs."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field

from cloud_content_hub.application.shared.dto.base import ApplicationDto, ResourceBaseDto


class SystemHealthStatusDto(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"


class DependencyHealthStatusDto(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class DependencyStatusDto(ApplicationDto):
    """Single dependency health projection."""

    name: str
    status: DependencyHealthStatusDto


class SystemStatusResponse(ApplicationDto):
    """Operational system status returned by administration queries."""

    status: SystemHealthStatusDto
    version: str
    started_at: datetime
    dependencies: tuple[DependencyStatusDto, ...]
    maintenance_enabled: bool = False


class ProviderTypeDto(StrEnum):
    AI = "ai"
    SOCIAL = "social"
    STORAGE = "storage"
    NOTIFICATION = "notification"
    IDENTITY = "identity"


class ProviderOperationalStatusDto(StrEnum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    DEGRADED = "degraded"


class ProviderHealthResponse(ApplicationDto):
    """Normalized provider health projection."""

    provider_type: ProviderTypeDto
    code: str
    name: str
    status: ProviderOperationalStatusDto
    checked_at: datetime
    message: str | None = None


class AdminQueueNameDto(StrEnum):
    AI = "ai"
    MEDIA = "media"
    NOTIFICATION = "notification"
    MAINTENANCE = "maintenance"
    PUBLISHING = "publishing"


class QueueStatusResponse(ApplicationDto):
    """Aggregate queue depth and age projection."""

    queue_name: AdminQueueNameDto
    queued: int = Field(ge=0)
    running: int = Field(ge=0)
    retry_wait: int = Field(ge=0)
    failed: int = Field(ge=0)
    dead_lettered: int = Field(ge=0)
    oldest_queued_at: datetime | None = None


class StorageHealthStatusDto(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class StorageStatusResponse(ApplicationDto):
    """Storage subsystem health projection."""

    status: StorageHealthStatusDto
    provider_code: str
    checked_at: datetime
    container_count: int = Field(ge=0)
    message: str | None = None


class UserStatusDto(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    ANONYMIZED = "anonymized"


class UserSummaryResponse(ResourceBaseDto):
    """Administrative user summary projection."""

    email: str | None
    display_name: str
    locale: str
    time_zone: str
    status: UserStatusDto


class WorkspaceStatusDto(StrEnum):
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSING = "closing"
    CLOSED = "closed"


class WorkspaceSummaryResponse(ResourceBaseDto):
    """Administrative workspace summary projection."""

    organization_id: UUID
    name: str
    slug: str
    status: WorkspaceStatusDto
    time_zone: str
    retention_policy_days: int | None = None


class AuditOutcomeDto(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"


class AuditEntryDto(ApplicationDto):
    """Single audit log entry projection."""

    id: UUID
    workspace_id: UUID | None
    organization_id: UUID | None
    actor_user_id: UUID | None
    action: str
    target_type: str
    target_id: UUID | None
    outcome: AuditOutcomeDto
    source: str
    occurred_at: datetime


class AuditSummaryResponse(ApplicationDto):
    """Aggregated audit query result."""

    total_count: int = Field(ge=0)
    success_count: int = Field(ge=0)
    failure_count: int = Field(ge=0)
    denied_count: int = Field(ge=0)
    recent_entries: tuple[AuditEntryDto, ...]


class FeatureFlagResponse(ApplicationDto):
    """Read-only feature flag projection."""

    key: str
    enabled: bool
    description: str
    owner: str | None = None
    purpose: str | None = None
    expires_at: datetime | None = None


class ApplicationConfigResponse(ApplicationDto):
    """Read-only non-secret application configuration entry."""

    key: str
    value: Any
    value_type: str
    scope_type: str
    description: str


class MaintenanceModeStateResponse(ApplicationDto):
    """Global maintenance mode state."""

    enabled: bool
    message: str | None = None
    updated_at: datetime
    updated_by: UUID | None = None
