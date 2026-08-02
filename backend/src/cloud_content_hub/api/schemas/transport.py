"""Transport-only request and response models for OpenAPI and HTTP validation."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field, model_validator

from cloud_content_hub.api.responses import ApiModel
from cloud_content_hub.application.scheduler.dto.requests import (
    AmbiguityPolicyDto,
    DstFoldDto,
    SchedulePriorityDto,
)


class UpdateContentRequest(ApiModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    body_text: str | None = None
    body_rich: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    summary: str | None = None
    lifecycle_status: str | None = None

    @model_validator(mode="after")
    def validate_nonempty_patch(self) -> UpdateContentRequest:
        if not any(
            value is not None
            for value in (
                self.title,
                self.body_text,
                self.body_rich,
                self.metadata,
                self.summary,
                self.lifecycle_status,
            )
        ):
            msg = "At least one field must be provided."
            raise ValueError(msg)
        return self


class UpdateScheduleRequest(ApiModel):
    requested_local_at: datetime | None = None
    time_zone: str | None = Field(default=None, min_length=1)
    fold: DstFoldDto | None = None
    ambiguity_policy: AmbiguityPolicyDto | None = None
    priority: SchedulePriorityDto | None = None
    state: str | None = Field(default=None, pattern=r"^(scheduled|paused)$")

    @model_validator(mode="after")
    def validate_nonempty_patch(self) -> UpdateScheduleRequest:
        if not any(
            value is not None
            for value in (
                self.requested_local_at,
                self.time_zone,
                self.fold,
                self.ambiguity_policy,
                self.priority,
                self.state,
            )
        ):
            msg = "At least one field must be provided."
            raise ValueError(msg)
        return self


class PublicationHistoryItemDto(ApiModel):
    id: UUID
    publication_id: UUID
    target_id: UUID
    state_type: str
    from_state: str | None = None
    to_state: str
    reason_code: str | None = None
    occurred_at: datetime


class JobStateDto(StrEnum):
    QUEUED = "queued"
    LEASED = "leased"
    RUNNING = "running"
    RETRY_WAIT = "retry_wait"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    DEAD_LETTERED = "dead_lettered"
    CANCELLED = "cancelled"


class JobDto(ApiModel):
    id: UUID
    version: int = Field(ge=1)
    created_at: datetime
    updated_at: datetime
    job_type: str
    queue_name: str
    state: JobStateDto
    resource_type: str | None = None
    resource_id: UUID | None = None
    attempt_count: int = Field(ge=0)
    max_attempts: int = Field(ge=1)
    available_at: datetime
    completed_at: datetime | None = None
    error_code: str | None = None


class HealthDto(ApiModel):
    status: str
    version: str


class ProbeDto(ApiModel):
    status: str
