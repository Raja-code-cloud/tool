"""Publishing response DTOs."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from cloud_content_hub.application.shared.dto.base import ApplicationDto, ResourceBaseDto


class PublicationStatusDto(StrEnum):
    DRAFT = "draft"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PARTIALLY_FAILED = "partially_failed"
    CANCELLED = "cancelled"


class ApprovalStateDto(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"
    CANCELLED = "cancelled"


class PublicationTargetDto(ApplicationDto):
    """Publication target projection."""

    id: UUID
    social_account_id: UUID
    platform_id: UUID
    approval_state: ApprovalStateDto
    external_post_id: str | None = None
    external_url: str | None = None
    published_at: datetime | None = None


class PublicationDto(ResourceBaseDto):
    """Publication projection returned by handlers."""

    asset_id: UUID
    content_version_id: UUID
    approval_request_id: UUID | None
    title: str
    status: PublicationStatusDto
    targets: tuple[PublicationTargetDto, ...]
