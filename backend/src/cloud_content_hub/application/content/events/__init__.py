"""Content domain events raised by command handlers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from cloud_content_hub.application.content.interfaces.content_repository import ContentOrigin


@dataclass(frozen=True, slots=True)
class ContentGenerated:
    """Raised when AI content generation is accepted and queued."""

    workspace_id: UUID
    content_id: UUID
    asset_id: UUID
    generation_request_id: UUID
    actor_id: UUID
    scope: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class ContentRegenerated:
    """Raised when AI content regeneration is accepted and queued."""

    workspace_id: UUID
    content_id: UUID
    asset_id: UUID
    generation_request_id: UUID
    actor_id: UUID
    scope: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class ContentArchived:
    """Raised when content is transitioned to archived lifecycle status."""

    workspace_id: UUID
    content_id: UUID
    actor_id: UUID
    version: int
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class ContentDeleted:
    """Raised when content is soft-deleted."""

    workspace_id: UUID
    content_id: UUID
    actor_id: UUID
    version: int
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class ContentApproved:
    """Raised when a generation output is approved and materialized."""

    workspace_id: UUID
    content_id: UUID
    output_id: UUID
    version_id: UUID
    actor_id: UUID
    origin: ContentOrigin
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class ContentRejected:
    """Raised when a generation output is rejected."""

    workspace_id: UUID
    content_id: UUID
    output_id: UUID
    actor_id: UUID
    reason: str | None
    occurred_at: datetime


ContentDomainEvent = (
    ContentGenerated
    | ContentRegenerated
    | ContentArchived
    | ContentDeleted
    | ContentApproved
    | ContentRejected
)

__all__ = [
    "ContentApproved",
    "ContentArchived",
    "ContentDeleted",
    "ContentDomainEvent",
    "ContentGenerated",
    "ContentRegenerated",
    "ContentRejected",
]
