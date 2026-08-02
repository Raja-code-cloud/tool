"""Publication record to DTO mappers."""

from __future__ import annotations

from cloud_content_hub.application.publishing.dto.responses import (
    ApprovalStateDto,
    PublicationDto,
    PublicationStatusDto,
    PublicationTargetDto,
)
from cloud_content_hub.application.publishing.interfaces.publication_repository import (
    PublicationRecord,
)


class PublicationMapper:
    """Maps publication read models to response DTOs."""

    @staticmethod
    def to_dto(record: PublicationRecord) -> PublicationDto:
        return PublicationDto(
            id=record.id,
            version=record.version,
            created_at=record.created_at,
            updated_at=record.updated_at,
            asset_id=record.asset_id,
            content_version_id=record.content_version_id,
            approval_request_id=record.approval_request_id,
            title=record.title,
            status=PublicationStatusDto(record.status.value),
            targets=tuple(
                PublicationTargetDto(
                    id=target.id,
                    social_account_id=target.social_account_id,
                    platform_id=target.platform_id,
                    approval_state=ApprovalStateDto(target.approval_state.value),
                    external_post_id=target.external_post_id,
                    external_url=target.external_url,
                    published_at=target.published_at,
                )
                for target in record.targets
            ),
        )
