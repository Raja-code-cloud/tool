"""Publishing repository port and read models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class PublicationStatus(StrEnum):
    DRAFT = "draft"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PARTIALLY_FAILED = "partially_failed"
    CANCELLED = "cancelled"


class ApprovalState(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class PublicationTargetRecord:
    """Publication target read model."""

    id: UUID
    social_account_id: UUID
    platform_id: UUID
    approval_state: ApprovalState
    external_post_id: str | None
    external_url: str | None
    published_at: datetime | None


@dataclass(frozen=True, slots=True)
class PublicationRecord:
    """Publication aggregate read model."""

    id: UUID
    workspace_id: UUID
    version: int
    created_at: datetime
    updated_at: datetime
    asset_id: UUID
    content_version_id: UUID
    approval_request_id: UUID | None
    title: str
    status: PublicationStatus
    targets: tuple[PublicationTargetRecord, ...]


@dataclass(frozen=True, slots=True)
class NewPublicationTarget:
    """Input for creating a publication target."""

    social_account_id: UUID
    generation_output_id: UUID | None


@dataclass(frozen=True, slots=True)
class NewPublication:
    """Input for creating a publication."""

    workspace_id: UUID
    asset_id: UUID
    content_version_id: UUID
    title: str
    targets: tuple[NewPublicationTarget, ...]
    created_by: UUID


@dataclass(frozen=True, slots=True)
class PublicationHistoryRecord:
    """Publication status history read model."""

    id: UUID
    publication_id: UUID
    target_id: UUID
    state_type: str
    from_state: str | None
    to_state: str
    reason_code: str | None
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class PublicationHistoryCriteria:
    """Filters for listing publication status history."""

    workspace_id: UUID
    cursor: str | None
    limit: int
    occurred_after: datetime | None
    occurred_before: datetime | None
    states: frozenset[str]
    content_id: UUID | None
    platform_id: UUID | None
    social_account_id: UUID | None
    sort: str


@dataclass(frozen=True, slots=True)
class PublicationHistoryPage:
    """Paged publication history result."""

    items: tuple[PublicationHistoryRecord, ...]
    next_cursor: str | None
    has_more: bool


class IPublicationRepository(Protocol):
    """Repository port for publications."""

    async def get_by_id(
        self, *, workspace_id: UUID, publication_id: UUID
    ) -> PublicationRecord | None:
        """Return one active publication."""

    async def create(self, publication: NewPublication) -> PublicationRecord:
        """Persist a new publication aggregate."""

    async def update_status(
        self,
        *,
        workspace_id: UUID,
        publication_id: UUID,
        status: PublicationStatus,
        expected_version: int,
        updated_by: UUID,
    ) -> PublicationRecord:
        """Update publication status with optimistic concurrency."""

    async def validate_content_version(
        self,
        *,
        workspace_id: UUID,
        content_id: UUID,
        content_version_id: UUID,
    ) -> tuple[UUID, bool]:
        """Return asset id and whether the version is approved and immutable."""

    async def validate_social_accounts(
        self,
        *,
        workspace_id: UUID,
        social_account_ids: frozenset[UUID],
    ) -> bool:
        """Return whether all social accounts are healthy and enabled."""

    async def list_publication_history(
        self, criteria: PublicationHistoryCriteria
    ) -> PublicationHistoryPage:
        """List publication status history for a workspace."""
