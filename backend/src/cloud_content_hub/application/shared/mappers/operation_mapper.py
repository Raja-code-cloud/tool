"""Shared operation mappers."""

from __future__ import annotations

from cloud_content_hub.application.shared.dto.base import (
    OperationDto,
    OperationStatus,
    OperationType,
)
from cloud_content_hub.application.shared.interfaces.job_queue import (
    BackgroundJobRecord,
    JobQueueName,
)


def map_upload_operation(job: BackgroundJobRecord) -> OperationDto:
    """Map a media upload background job to an operation DTO."""

    return OperationDto(
        id=job.id,
        version=job.version,
        created_at=job.created_at,
        updated_at=job.updated_at,
        type=OperationType.UPLOAD,
        status=OperationStatus(job.state.value),
        resource_type=job.resource_type,
        resource_id=job.resource_id,
        error_code=job.error_code,
    )


def map_generation_operation(job: BackgroundJobRecord) -> OperationDto:
    """Map an AI generation background job to an operation DTO."""

    return OperationDto(
        id=job.id,
        version=job.version,
        created_at=job.created_at,
        updated_at=job.updated_at,
        type=OperationType.GENERATION,
        status=OperationStatus(job.state.value),
        resource_type=job.resource_type,
        resource_id=job.resource_id,
        error_code=job.error_code,
    )


def map_publishing_operation(job: BackgroundJobRecord) -> OperationDto:
    """Map a publishing background job to an operation DTO."""

    return OperationDto(
        id=job.id,
        version=job.version,
        created_at=job.created_at,
        updated_at=job.updated_at,
        type=OperationType.PUBLISHING,
        status=OperationStatus(job.state.value),
        resource_type=job.resource_type,
        resource_id=job.resource_id,
        error_code=job.error_code,
    )


def queue_name_for_upload() -> JobQueueName:
    return JobQueueName.MEDIA
