"""Versioned JSON event envelope and outbox record models."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

EVENT_SCHEMA_VERSION = 1


class EventMetadata(BaseModel):
    """Cross-cutting identifiers propagated with every integration event."""

    model_config = ConfigDict(frozen=True)

    correlation_id: str | None = None
    trace_id: str | None = None
    span_id: str | None = None
    request_id: str | None = None
    source: str = "cloud_content_hub"
    content_type: str = "application/json"


class EventEnvelope(BaseModel):
    """Wire-format envelope delivered to Celery workers and platform consumers."""

    model_config = ConfigDict(frozen=True)

    schema_version: int = Field(default=EVENT_SCHEMA_VERSION, ge=1)
    event_id: UUID
    event_type: str
    event_version: int = Field(ge=1)
    aggregate_type: str
    aggregate_id: UUID
    workspace_id: UUID | None = None
    organization_id: UUID | None = None
    occurred_at: datetime
    published_at: datetime | None = None
    payload: dict[str, Any]
    metadata: EventMetadata
    headers: dict[str, Any] = Field(default_factory=dict)


class OutboxAppendRequest(BaseModel):
    """Input required to persist one transactional outbox row."""

    model_config = ConfigDict(frozen=True)

    workspace_id: UUID | None
    organization_id: UUID | None
    aggregate_type: str
    aggregate_id: UUID
    event_type: str
    event_version: int = Field(ge=1)
    payload: dict[str, Any]
    headers: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime
    available_at: datetime
    created_by: UUID | None = None


class OutboxDispatchRecord(BaseModel):
    """Read model returned when claiming due outbox events for dispatch."""

    model_config = ConfigDict(frozen=True)

    id: UUID
    workspace_id: UUID | None
    organization_id: UUID | None
    aggregate_type: str
    aggregate_id: UUID
    event_type: str
    event_version: int
    payload: dict[str, Any]
    headers: dict[str, Any]
    occurred_at: datetime
    available_at: datetime
    attempt_count: int
    last_error: str | None
