"""Deterministic DTO factories for API and regression tests."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from cloud_content_hub.application.administration.dto.responses import (
    DependencyHealthStatusDto,
    DependencyStatusDto,
    ProviderOperationalStatusDto,
    ProviderTypeDto,
    ProviderHealthResponse,
    QueueStatusResponse,
    AdminQueueNameDto,
    SystemHealthStatusDto,
    SystemStatusResponse,
)
from cloud_content_hub.application.analytics.dto.responses import (
    DashboardResponse,
    MetricValueDto,
    PlatformAnalyticsResponse,
    PostAnalyticsResponse,
)
from cloud_content_hub.application.assets.dto.responses import (
    AssetDto,
    AssetLifecycleStatusDto,
    AssetTypeDto,
)
from cloud_content_hub.application.content.dto.responses import (
    ContentDto,
    ContentLifecycleStatusDto,
    ContentOriginDto,
)
from cloud_content_hub.application.notifications.dto.responses import (
    NotificationResponseDto,
    NotificationSeverityDto,
)
from cloud_content_hub.application.publishing.dto.responses import (
    ApprovalStateDto,
    PublicationDto,
    PublicationStatusDto,
    PublicationTargetDto,
)
from cloud_content_hub.application.scheduler.dto.responses import (
    AmbiguityPolicyDto,
    ScheduleDto,
    SchedulePriorityDto,
    ScheduleStateDto,
)
from cloud_content_hub.application.shared.dto.base import (
    OperationDto,
    OperationStatus,
    OperationType,
    PageInfoDto,
    PagedResultDto,
)
from cloud_content_hub.api.schemas.transport import JobDto, JobStateDto, PublicationHistoryItemDto

FIXED_NOW = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)
DEFAULT_WORKSPACE_ID = UUID("01900000-0000-7000-8000-000000000001")
DEFAULT_USER_ID = UUID("01900000-0000-7000-8000-000000000010")


def _resource_ids() -> tuple[UUID, UUID, UUID]:
    return uuid4(), uuid4(), uuid4()


def asset_dto(
    *,
    asset_id: UUID | None = None,
    owner_id: UUID = DEFAULT_USER_ID,
    title: str = "Regression Asset",
) -> AssetDto:
    resolved_id = asset_id or uuid4()
    return AssetDto(
        id=resolved_id,
        version=1,
        created_at=FIXED_NOW,
        updated_at=FIXED_NOW,
        asset_type=AssetTypeDto.POSTER,
        title=title,
        summary=None,
        lifecycle_status=AssetLifecycleStatusDto.ACTIVE,
        owner_id=owner_id,
        is_favorite=False,
    )


def content_dto(*, asset_id: UUID | None = None) -> ContentDto:
    resolved_asset_id = asset_id or uuid4()
    return ContentDto(
        id=uuid4(),
        version=1,
        created_at=FIXED_NOW,
        updated_at=FIXED_NOW,
        asset_id=resolved_asset_id,
        title="Generated Content",
        body_text="Deterministic regression body.",
        metadata={},
        lifecycle_status=ContentLifecycleStatusDto.ACTIVE,
        origin=ContentOriginDto.AI,
        content_version_id=uuid4(),
    )


def operation_dto(
    *,
    operation_type: OperationType = OperationType.UPLOAD,
    resource_id: UUID | None = None,
) -> OperationDto:
    return OperationDto(
        id=uuid4(),
        version=1,
        created_at=FIXED_NOW,
        updated_at=FIXED_NOW,
        type=operation_type,
        status=OperationStatus.QUEUED,
        resource_type="asset",
        resource_id=resource_id or uuid4(),
    )


def publication_dto(*, asset_id: UUID | None = None, content_version_id: UUID | None = None) -> PublicationDto:
    target_id, platform_id, account_id = _resource_ids()
    return PublicationDto(
        id=uuid4(),
        version=1,
        created_at=FIXED_NOW,
        updated_at=FIXED_NOW,
        asset_id=asset_id or uuid4(),
        content_version_id=content_version_id or uuid4(),
        approval_request_id=None,
        title="Launch Publication",
        status=PublicationStatusDto.READY,
        targets=(
            PublicationTargetDto(
                id=target_id,
                social_account_id=account_id,
                platform_id=platform_id,
                approval_state=ApprovalStateDto.APPROVED,
            ),
        ),
    )


def schedule_dto(*, publication_target_id: UUID | None = None) -> ScheduleDto:
    return ScheduleDto(
        id=uuid4(),
        version=1,
        created_at=FIXED_NOW,
        updated_at=FIXED_NOW,
        publication_target_id=publication_target_id or uuid4(),
        requested_local_at=FIXED_NOW.replace(tzinfo=None),
        time_zone="UTC",
        fold=None,
        ambiguity_policy=AmbiguityPolicyDto.REJECT,
        scheduled_for=FIXED_NOW,
        state=ScheduleStateDto.SCHEDULED,
        priority=SchedulePriorityDto.NORMAL,
    )


def notification_dto() -> NotificationResponseDto:
    return NotificationResponseDto(
        id=uuid4(),
        version=1,
        created_at=FIXED_NOW,
        updated_at=FIXED_NOW,
        type_code="content.approved",
        title="Content approved",
        body="Your content was approved.",
        severity=NotificationSeverityDto.SUCCESS,
        read_at=None,
    )


def dashboard_dto() -> DashboardResponse:
    return DashboardResponse(
        period_start=FIXED_NOW,
        period_end=FIXED_NOW,
        time_zone="UTC",
        fresh_through=FIXED_NOW,
        methodology_version=1,
        metrics=(
            MetricValueDto(code="reach", value="1000", unit="count", is_estimated=False),
        ),
    )


def platform_analytics_dto() -> PlatformAnalyticsResponse:
    return PlatformAnalyticsResponse(
        platform_id=uuid4(),
        platform_code="linkedin",
        account_count=1,
        metrics=(MetricValueDto(code="impressions", value="500", unit="count", is_estimated=False),),
        fresh_through=FIXED_NOW,
    )


def post_analytics_dto(*, content_id: UUID | None = None) -> PostAnalyticsResponse:
    return PostAnalyticsResponse(
        content_id=content_id or uuid4(),
        snapshot_at=FIXED_NOW,
        reach=100,
        engagements=10,
        metrics=(MetricValueDto(code="engagement_rate", value="0.10", unit="ratio", is_estimated=False),),
    )


def system_status_dto() -> SystemStatusResponse:
    return SystemStatusResponse(
        status=SystemHealthStatusDto.HEALTHY,
        version="1.0.0-regression",
        started_at=FIXED_NOW,
        dependencies=(
            DependencyStatusDto(name="database", status=DependencyHealthStatusDto.HEALTHY),
            DependencyStatusDto(name="redis", status=DependencyHealthStatusDto.HEALTHY),
        ),
    )


def queue_status_dto() -> QueueStatusResponse:
    return QueueStatusResponse(
        queue_name=AdminQueueNameDto.MEDIA,
        queued=0,
        running=0,
        retry_wait=0,
        failed=0,
        dead_lettered=0,
    )


def provider_health_dto() -> ProviderHealthResponse:
    return ProviderHealthResponse(
        provider_type=ProviderTypeDto.AI,
        code="mock",
        name="Mock Provider",
        status=ProviderOperationalStatusDto.ENABLED,
        checked_at=FIXED_NOW,
    )


def job_dto() -> JobDto:
    return JobDto(
        id=uuid4(),
        version=1,
        created_at=FIXED_NOW,
        updated_at=FIXED_NOW,
        job_type="asset.upload",
        queue_name="media",
        state=JobStateDto.QUEUED,
        attempt_count=0,
        max_attempts=3,
        available_at=FIXED_NOW,
    )


def publication_history_item_dto() -> PublicationHistoryItemDto:
    return PublicationHistoryItemDto(
        id=uuid4(),
        publication_id=uuid4(),
        target_id=uuid4(),
        state_type="status",
        to_state="completed",
        occurred_at=FIXED_NOW,
    )


def empty_page[T](*, limit: int = 25) -> PagedResultDto[T]:
    return PagedResultDto(
        items=(),
        page=PageInfoDto(next_cursor=None, has_more=False, limit=limit),
    )


def single_page[T](item: T, *, limit: int = 25) -> PagedResultDto[T]:
    return PagedResultDto(
        items=(item,),
        page=PageInfoDto(next_cursor=None, has_more=False, limit=limit),
    )
