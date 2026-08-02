"""Publishing request DTOs."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from cloud_content_hub.application.shared.dto.base import ApplicationDto


class PublicationTargetRequestDto(ApplicationDto):
    """Target definition for publication creation."""

    social_account_id: UUID
    generation_output_id: UUID | None = None


class CreatePublicationRequestDto(ApplicationDto):
    """Request payload for creating a publication."""

    content_id: UUID
    content_version_id: UUID
    title: str = Field(min_length=1, max_length=300)
    targets: tuple[PublicationTargetRequestDto, ...] = Field(min_length=1)


class DispatchPublicationRequestDto(ApplicationDto):
    """Request payload for dispatching a publication."""

    target_ids: tuple[UUID, ...] | None = None
