"""Schedule time resolution port."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from cloud_content_hub.application.scheduler.interfaces.schedule_repository import AmbiguityPolicy


@dataclass(frozen=True, slots=True)
class LocalScheduleInput:
    """Local wall-time schedule input."""

    requested_local_at: datetime
    time_zone: str
    fold: int | None
    ambiguity_policy: AmbiguityPolicy


@dataclass(frozen=True, slots=True)
class ResolvedLocalTime:
    """Resolved UTC instant from local wall time."""

    scheduled_for: datetime
    fold: int | None


class IScheduleTimeResolver(Protocol):
    """Port for resolving local wall times to UTC."""

    def resolve(self, schedule: LocalScheduleInput) -> ResolvedLocalTime:
        """Resolve a local schedule to UTC, applying DST rules."""
