"""Shared application DTO primitives."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


def to_camel(value: str) -> str:
    """Convert snake_case field names to camelCase."""

    parts = value.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class ApplicationDto(BaseModel):
    """Base Pydantic model for application-layer DTOs."""

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )


class ResourceBaseDto(ApplicationDto):
    """Common resource identity and audit fields."""

    id: UUID
    version: int = Field(ge=1)
    created_at: datetime
    updated_at: datetime


class OperationType(StrEnum):
    GENERATION = "generation"
    PUBLISHING = "publishing"
    UPLOAD = "upload"
    ADMIN_JOB = "adminJob"


class OperationStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OperationDto(ResourceBaseDto):
    """Asynchronous operation projection returned by command handlers."""

    type: OperationType
    status: OperationStatus
    resource_type: str | None = None
    resource_id: UUID | None = None
    error_code: str | None = None


class PageInfoDto(ApplicationDto):
    """Cursor pagination metadata."""

    next_cursor: str | None = None
    has_more: bool = False
    limit: int = Field(ge=1, le=100)


class PagedResultDto[T](ApplicationDto):
    """Generic paged result envelope for query handlers."""

    items: tuple[T, ...]
    page: PageInfoDto


def build_page_info(*, next_cursor: str | None, has_more: bool, limit: int) -> PageInfoDto:
    """Build pagination metadata from a repository page."""

    return PageInfoDto(next_cursor=next_cursor, has_more=has_more, limit=limit)
