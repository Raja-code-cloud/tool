"""Save search command handler."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from cloud_content_hub.application.search.commands import SaveSearchCommand
from cloud_content_hub.application.search.dto.responses import SavedSearchResponse
from cloud_content_hub.application.search.events import SavedSearchCreated
from cloud_content_hub.application.search.interfaces.event_publisher import ISearchEventPublisher
from cloud_content_hub.application.search.interfaces.saved_search_repository import (
    ISavedSearchRepository,
    NewSavedSearch,
)
from cloud_content_hub.application.search.mappers.search_mapper import SearchMapper
from cloud_content_hub.application.search.validators.search_validator import (
    filters_to_spec,
    normalize_search_query,
    require_any_search_permission,
    validate_global_sort,
    validate_saved_search_name,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class SaveSearchHandler:
    """Persists a saved search for the current user."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        saved_search_repository_factory: Callable[[IUnitOfWork], ISavedSearchRepository],
        event_publisher: ISearchEventPublisher | None = None,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._saved_search_repository_factory = saved_search_repository_factory
        self._event_publisher = event_publisher

    async def handle(self, actor: ActorContext, command: SaveSearchCommand) -> SavedSearchResponse:
        require_any_search_permission(actor)
        name = validate_saved_search_name(command.request.name)
        query = normalize_search_query(command.request.query)
        validate_global_sort(command.request.sort)
        filter_spec = filters_to_spec(
            entity_types=(
                frozenset(entity.value for entity in command.request.filters.entity_types)
                if command.request.filters.entity_types
                else None
            ),
            asset_types=command.request.filters.asset_types,
            lifecycle_statuses=command.request.filters.lifecycle_statuses,
            content_origins=command.request.filters.content_origins,
            publication_statuses=command.request.filters.publication_statuses,
            owner_id=(
                str(command.request.filters.owner_id) if command.request.filters.owner_id else None
            ),
            project_id=(
                str(command.request.filters.project_id)
                if command.request.filters.project_id
                else None
            ),
            folder_id=(
                str(command.request.filters.folder_id)
                if command.request.filters.folder_id
                else None
            ),
            updated_after=command.request.filters.updated_after,
            updated_before=command.request.filters.updated_before,
        )

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._saved_search_repository_factory(unit_of_work)
            saved = await repository.create(
                NewSavedSearch(
                    workspace_id=actor.workspace_id,
                    owner_id=actor.user_id,
                    name=name,
                    query=query,
                    filter_spec=filter_spec,
                    sort=command.request.sort,
                    is_shared=command.request.is_shared,
                    created_by=actor.user_id,
                )
            )
            if self._event_publisher is not None:
                await self._event_publisher.publish(
                    SavedSearchCreated(
                        workspace_id=actor.workspace_id,
                        saved_search_id=saved.id,
                        owner_id=actor.user_id,
                        actor_id=actor.user_id,
                        name=name,
                        occurred_at=datetime.now(tz=UTC),
                    ),
                    unit_of_work=unit_of_work,
                )
            await unit_of_work.flush()

        return SearchMapper.to_saved_search_dto(saved)
