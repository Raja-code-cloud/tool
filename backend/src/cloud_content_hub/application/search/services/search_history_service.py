"""Search history orchestration service."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from cloud_content_hub.application.search.events import SearchExecuted
from cloud_content_hub.application.search.interfaces.event_publisher import ISearchEventPublisher
from cloud_content_hub.application.search.interfaces.recent_search_repository import (
    IRecentSearchRepository,
    NewRecentSearch,
)
from cloud_content_hub.application.search.interfaces.suggestion_repository import SearchEntityType
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class SearchHistoryService:
    """Records recent searches and emits search executed events."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        recent_search_repository_factory: Callable[[IUnitOfWork], IRecentSearchRepository],
        event_publisher: ISearchEventPublisher | None = None,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._recent_search_repository_factory = recent_search_repository_factory
        self._event_publisher = event_publisher

    async def record(
        self,
        actor: ActorContext,
        *,
        query: str,
        entity_types: frozenset[SearchEntityType],
        filter_spec: dict[str, Any],
        result_count: int,
    ) -> None:
        """Persist a recent search entry and optionally emit a domain event."""

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._recent_search_repository_factory(unit_of_work)
            spec = dict(filter_spec)
            if entity_types:
                spec.setdefault(
                    "entityTypes",
                    sorted(entity_type.value for entity_type in entity_types),
                )
            await repository.record(
                NewRecentSearch(
                    workspace_id=actor.workspace_id,
                    user_id=actor.user_id,
                    query=query,
                    filter_spec=spec,
                )
            )
            if self._event_publisher is not None:
                await self._event_publisher.publish(
                    SearchExecuted(
                        workspace_id=actor.workspace_id,
                        user_id=actor.user_id,
                        query=query,
                        entity_types=tuple(sorted(entity_types, key=lambda value: value.value)),
                        result_count=result_count,
                        filter_spec=spec,
                        occurred_at=datetime.now(tz=UTC),
                    ),
                    unit_of_work=unit_of_work,
                )
            await unit_of_work.flush()
