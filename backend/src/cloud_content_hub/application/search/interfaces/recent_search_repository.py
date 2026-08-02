"""Recent search history repository port and read models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RecentSearchRecord:
    """User recent search history entry."""

    id: UUID
    workspace_id: UUID
    user_id: UUID
    query: str
    filter_spec: dict[str, Any]
    executed_at: datetime


@dataclass(frozen=True, slots=True)
class NewRecentSearch:
    """Input for recording a recent search."""

    workspace_id: UUID
    user_id: UUID
    query: str
    filter_spec: dict[str, Any]


class IRecentSearchRepository(Protocol):
    """Repository port for per-user recent search history."""

    async def list_for_user(
        self,
        *,
        workspace_id: UUID,
        user_id: UUID,
        limit: int = 10,
    ) -> tuple[RecentSearchRecord, ...]:
        """Return recent searches for the user ordered by most recent first."""

    async def record(self, entry: NewRecentSearch) -> RecentSearchRecord:
        """Record or bump a recent search entry for the user."""

    async def clear_for_user(
        self,
        *,
        workspace_id: UUID,
        user_id: UUID,
    ) -> int:
        """Clear all recent searches for the user and return the number removed."""
