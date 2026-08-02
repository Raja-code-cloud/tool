"""Delete saved search command handler."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from cloud_content_hub.application.search.commands import DeleteSavedSearchCommand
from cloud_content_hub.application.search.events import SavedSearchDeleted
from cloud_content_hub.application.search.exceptions.search_errors import SavedSearchNotFoundError
from cloud_content_hub.application.search.interfaces.event_publisher import ISearchEventPublisher
from cloud_content_hub.application.search.interfaces.saved_search_repository import (
    ISavedSearchRepository,
)
from cloud_content_hub.application.search.validators.search_validator import (
    require_any_search_permission,
    validate_saved_search_owner,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.core.errors import VersionConflictError


class DeleteSavedSearchHandler:
    """Soft-deletes a saved search owned by the current user."""

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

    async def handle(self, actor: ActorContext, command: DeleteSavedSearchCommand) -> None:
        require_any_search_permission(actor)

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._saved_search_repository_factory(unit_of_work)
            saved = await repository.get_by_id(
                workspace_id=actor.workspace_id,
                saved_search_id=command.saved_search_id,
            )
            if saved is None:
                raise SavedSearchNotFoundError(
                    parameters={"savedSearchId": str(command.saved_search_id)},
                )
            validate_saved_search_owner(saved, actor=actor)
            if saved.version != command.expected_version:
                raise VersionConflictError(
                    parameters={
                        "savedSearchId": str(command.saved_search_id),
                        "expectedVersion": command.expected_version,
                    },
                )
            await repository.soft_delete(
                workspace_id=actor.workspace_id,
                saved_search_id=command.saved_search_id,
                expected_version=command.expected_version,
                updated_by=actor.user_id,
            )
            if self._event_publisher is not None:
                await self._event_publisher.publish(
                    SavedSearchDeleted(
                        workspace_id=actor.workspace_id,
                        saved_search_id=command.saved_search_id,
                        owner_id=saved.owner_id,
                        actor_id=actor.user_id,
                        version=command.expected_version,
                        occurred_at=datetime.now(tz=UTC),
                    ),
                    unit_of_work=unit_of_work,
                )
            await unit_of_work.flush()
