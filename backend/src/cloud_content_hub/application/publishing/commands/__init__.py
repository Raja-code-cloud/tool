"""Publishing command definitions."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from cloud_content_hub.application.publishing.dto.requests import (
    CreatePublicationRequestDto,
    DispatchPublicationRequestDto,
)


@dataclass(frozen=True, slots=True)
class PublishContentCommand:
    """Command to create a publication."""

    request: CreatePublicationRequestDto
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class DispatchPublicationCommand:
    """Command to dispatch an existing publication."""

    publication_id: UUID
    expected_version: int
    request: DispatchPublicationRequestDto
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class CancelPublicationCommand:
    """Command to cancel a publication."""

    publication_id: UUID
    expected_version: int
