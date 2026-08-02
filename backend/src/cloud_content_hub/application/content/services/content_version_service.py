"""Content version lifecycle orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from cloud_content_hub.application.content.interfaces.content_repository import (
    ContentOrigin,
    ContentRecord,
    ContentVersionDetailRecord,
    IContentRepository,
    NewContentVersion,
)


@dataclass(frozen=True, slots=True)
class ContentVersionService:
    """Coordinates immutable version creation and aggregate projection updates."""

    async def create_user_version(
        self,
        repository: IContentRepository,
        *,
        content: ContentRecord,
        title: str,
        body_text: str | None,
        body_rich: dict[str, object] | None,
        metadata: dict[str, object],
        source_version_id: UUID | None,
        change_summary: str | None,
        actor_id: UUID,
    ) -> tuple[ContentVersionDetailRecord, ContentRecord]:
        """Create a user-origin version and update the aggregate pointer."""

        version = await repository.create_version(
            NewContentVersion(
                workspace_id=content.workspace_id,
                asset_id=content.asset_id,
                source_version_id=source_version_id,
                title=title,
                body_text=body_text,
                body_rich=body_rich,
                metadata=metadata,
                origin=ContentOrigin.USER,
                change_summary=change_summary,
                created_by=actor_id,
            )
        )
        updated = await repository.set_current_version(
            workspace_id=content.workspace_id,
            content_id=content.id,
            version_id=version.id,
            expected_version=content.version,
            updated_by=actor_id,
        )
        return version, updated

    async def materialize_generation_output(
        self,
        repository: IContentRepository,
        *,
        content: ContentRecord,
        version: ContentVersionDetailRecord,
        actor_id: UUID,
    ) -> ContentRecord:
        """Point the aggregate at a newly materialized AI version."""

        return await repository.set_current_version(
            workspace_id=content.workspace_id,
            content_id=content.id,
            version_id=version.id,
            expected_version=content.version,
            updated_by=actor_id,
        )
