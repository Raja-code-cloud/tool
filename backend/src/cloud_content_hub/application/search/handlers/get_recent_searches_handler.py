"""Recent searches query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.search.dto.responses import RecentSearchResponse
from cloud_content_hub.application.search.interfaces.recent_search_repository import (
    IRecentSearchRepository,
)
from cloud_content_hub.application.search.mappers.search_mapper import SearchMapper
from cloud_content_hub.application.search.queries import GetRecentSearchesQuery
from cloud_content_hub.application.search.validators.search_validator import (
    require_any_search_permission,
    validate_recent_search_limit,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class GetRecentSearchesHandler:
    """Returns recent searches for the authenticated user."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        recent_search_repository_factory: Callable[[IUnitOfWork], IRecentSearchRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._recent_search_repository_factory = recent_search_repository_factory

    async def handle(
        self,
        actor: ActorContext,
        query: GetRecentSearchesQuery,
    ) -> tuple[RecentSearchResponse, ...]:
        require_any_search_permission(actor)
        validate_recent_search_limit(query.limit)

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._recent_search_repository_factory(unit_of_work)
            records = await repository.list_for_user(
                workspace_id=actor.workspace_id,
                user_id=actor.user_id,
                limit=query.limit,
            )

        return tuple(SearchMapper.to_recent_search_dto(record) for record in records)
