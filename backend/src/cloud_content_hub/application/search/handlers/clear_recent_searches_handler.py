"""Clear recent searches command handler."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from cloud_content_hub.application.search.commands import ClearRecentSearchesCommand
from cloud_content_hub.application.search.events import RecentSearchCleared
from cloud_content_hub.application.search.interfaces.event_publisher import ISearchEventPublisher
from cloud_content_hub.application.search.interfaces.recent_search_repository import (
    IRecentSearchRepository,
)
from cloud_content_hub.application.search.validators.search_validator import (
    require_any_search_permission,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class ClearRecentSearchesHandler:
    """Clears recent search history for the authenticated user."""

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

    async def handle(self, actor: ActorContext, command: ClearRecentSearchesCommand) -> int:
        del command
        require_any_search_permission(actor)

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._recent_search_repository_factory(unit_of_work)
            cleared_count = await repository.clear_for_user(
                workspace_id=actor.workspace_id,
                user_id=actor.user_id,
            )
            if self._event_publisher is not None:
                await self._event_publisher.publish(
                    RecentSearchCleared(
                        workspace_id=actor.workspace_id,
                        user_id=actor.user_id,
                        actor_id=actor.user_id,
                        cleared_count=cleared_count,
                        occurred_at=datetime.now(tz=UTC),
                    ),
                    unit_of_work=unit_of_work,
                )
            await unit_of_work.flush()

        return cleared_count
