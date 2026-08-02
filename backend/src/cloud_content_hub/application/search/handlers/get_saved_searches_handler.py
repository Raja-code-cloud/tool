"""Saved searches query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.search.dto.responses import SavedSearchResponse
from cloud_content_hub.application.search.interfaces.saved_search_repository import (
    ISavedSearchRepository,
)
from cloud_content_hub.application.search.mappers.search_mapper import SearchMapper
from cloud_content_hub.application.search.queries import GetSavedSearchesQuery
from cloud_content_hub.application.search.validators.search_validator import (
    require_any_search_permission,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class GetSavedSearchesHandler:
    """Returns saved searches visible to the authenticated user."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        saved_search_repository_factory: Callable[[IUnitOfWork], ISavedSearchRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._saved_search_repository_factory = saved_search_repository_factory

    async def handle(
        self,
        actor: ActorContext,
        query: GetSavedSearchesQuery,
    ) -> tuple[SavedSearchResponse, ...]:
        require_any_search_permission(actor)

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._saved_search_repository_factory(unit_of_work)
            records = await repository.list_for_workspace(
                workspace_id=actor.workspace_id,
                owner_id=actor.user_id,
                include_shared=query.include_shared,
            )

        return tuple(SearchMapper.to_saved_search_dto(record) for record in records)
