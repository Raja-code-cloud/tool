"""Scheduler command definitions."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from cloud_content_hub.application.scheduler.dto.requests import ScheduleRequestDto


@dataclass(frozen=True, slots=True)
class SchedulePublicationCommand:
    """Command to schedule a publication target."""

    request: ScheduleRequestDto
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class CancelScheduleCommand:
    """Command to cancel a schedule."""

    schedule_id: UUID
    expected_version: int
