"""Content record to DTO mappers."""

from __future__ import annotations

from cloud_content_hub.application.content.dto.responses import (
    ContentDto,
    ContentLifecycleStatusDto,
    ContentOriginDto,
    ContentPreviewResponse,
    ContentVersionResponse,
    GenerationOutputDto,
    GenerationOutputStatusDto,
    PlatformContentDto,
    SeoMetadataDto,
    VersionComparisonResponse,
)
from cloud_content_hub.application.content.interfaces.content_repository import (
    ContentRecord,
    ContentVersionDetailRecord,
    GenerationOutputRecord,
    VersionComparisonRecord,
)
from cloud_content_hub.application.content.interfaces.platforms import ContentPlatform
from cloud_content_hub.application.shared.dto.base import OperationDto


class ContentMapper:
    """Maps content read models to response DTOs."""

    @staticmethod
    def to_dto(record: ContentRecord) -> ContentDto:
        return ContentDto(
            id=record.id,
            version=record.version,
            created_at=record.created_at,
            updated_at=record.updated_at,
            asset_id=record.asset_id,
            title=record.title,
            body_text=record.body_text,
            body_rich=record.body_rich,
            metadata=record.metadata,
            lifecycle_status=ContentLifecycleStatusDto(record.lifecycle_status.value),
            origin=ContentOriginDto(record.origin.value),
            content_version_id=record.content_version_id,
        )

    @staticmethod
    def to_version_dto(record: ContentVersionDetailRecord) -> ContentVersionResponse:
        return ContentVersionResponse(
            id=record.id,
            version=1,
            created_at=record.created_at,
            updated_at=record.created_at,
            asset_id=record.asset_id,
            version_number=record.version_number,
            title=record.title,
            body_text=record.body_text,
            body_rich=record.body_rich,
            metadata=record.metadata,
            origin=ContentOriginDto(record.origin.value),
            source_version_id=record.source_version_id,
            change_summary=record.change_summary,
            created_by=record.created_by,
        )

    @staticmethod
    def to_generation_output_dto(record: GenerationOutputRecord) -> GenerationOutputDto:
        return GenerationOutputDto(
            id=record.id,
            version=1,
            created_at=record.created_at,
            updated_at=record.created_at,
            generation_request_id=record.generation_request_id,
            sequence_no=record.sequence_no,
            platform_id=record.platform_id,
            output_text=record.output_text,
            output_metadata=record.output_metadata,
            safety_status=record.safety_status,
            materialized_version_id=record.materialized_version_id,
            status=GenerationOutputStatusDto(record.status.value),
        )

    @staticmethod
    def to_comparison_dto(record: VersionComparisonRecord) -> VersionComparisonResponse:
        return VersionComparisonResponse(
            source_version_id=record.source_version_id,
            target_version_id=record.target_version_id,
            title_changed=record.title_changed,
            body_changed=record.body_changed,
            metadata_changed=record.metadata_changed,
            source_title=record.source_title,
            target_title=record.target_title,
            source_body_text=record.source_body_text,
            target_body_text=record.target_body_text,
        )

    @staticmethod
    def to_generate_response(operation: OperationDto) -> dict[str, object]:
        return {
            "operationId": operation.id,
            "status": operation.status.value,
            "resourceType": operation.resource_type,
            "resourceId": operation.resource_id,
            "createdAt": operation.created_at,
        }

    @staticmethod
    def to_preview_response(
        *,
        platforms: tuple[PlatformContentDto, ...],
        seo_metadata: SeoMetadataDto | None = None,
    ) -> ContentPreviewResponse:
        return ContentPreviewResponse(
            platforms=platforms,
            seo_metadata=seo_metadata,
        )

    @staticmethod
    def platform_text(platform: ContentPlatform, text: str) -> PlatformContentDto:
        return PlatformContentDto(platform=platform, text=text)
