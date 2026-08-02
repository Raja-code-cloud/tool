"""Content command definitions."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from cloud_content_hub.application.content.dto.requests import (
    ApproveContentRequestDto,
    CreateContentVersionRequestDto,
    DuplicateContentRequestDto,
    GenerationRequestDto,
    RegenerationRequestDto,
    RejectContentRequestDto,
)


@dataclass(frozen=True, slots=True)
class GenerateContentCommand:
    """Command to request AI content generation."""

    request: GenerationRequestDto
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RegenerateContentCommand:
    """Command to request AI content regeneration."""

    request: RegenerationRequestDto
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class DuplicateContentCommand:
    """Command to duplicate content from an existing aggregate."""

    content_id: UUID
    request: DuplicateContentRequestDto
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class ArchiveContentCommand:
    """Command to archive content."""

    content_id: UUID
    expected_version: int


@dataclass(frozen=True, slots=True)
class DeleteContentCommand:
    """Command to soft-delete content."""

    content_id: UUID
    expected_version: int


@dataclass(frozen=True, slots=True)
class RestoreContentCommand:
    """Command to restore soft-deleted content."""

    content_id: UUID
    expected_version: int


@dataclass(frozen=True, slots=True)
class CreateContentVersionCommand:
    """Command to create a user-origin content version."""

    content_id: UUID
    expected_version: int
    request: CreateContentVersionRequestDto


@dataclass(frozen=True, slots=True)
class ApproveContentCommand:
    """Command to approve a generation output and materialize a version."""

    content_id: UUID
    expected_version: int
    request: ApproveContentRequestDto


@dataclass(frozen=True, slots=True)
class RejectContentCommand:
    """Command to reject a generation output."""

    content_id: UUID
    expected_version: int
    request: RejectContentRequestDto
