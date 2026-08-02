"""Restore content command handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.content.commands import RestoreContentCommand
from cloud_content_hub.application.content.dto.responses import ContentDto
from cloud_content_hub.application.content.interfaces.content_repository import IContentRepository
from cloud_content_hub.application.content.mappers.content_mapper import ContentMapper
from cloud_content_hub.application.content.validators.content_validator import validate_restore
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.core.errors import VersionConflictError


class RestoreContentHandler:
    """Orchestrates content restoration."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        content_repository_factory: Callable[[IUnitOfWork], IContentRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._content_repository_factory = content_repository_factory

    async def handle(self, actor: ActorContext, command: RestoreContentCommand) -> ContentDto:
        require_permission(actor, "content:write")

        async with self._unit_of_work_factory() as unit_of_work:
            content_repository = self._content_repository_factory(unit_of_work)
            content = await content_repository.get_deleted_by_id(
                workspace_id=actor.workspace_id,
                content_id=command.content_id,
            )
            content = validate_restore(content)
            assert content is not None
            if content.version != command.expected_version:
                raise VersionConflictError(
                    parameters={
                        "contentId": str(command.content_id),
                        "expectedVersion": command.expected_version,
                    },
                )

            restored = await content_repository.restore(
                workspace_id=actor.workspace_id,
                content_id=command.content_id,
                expected_version=command.expected_version,
                updated_by=actor.user_id,
            )
            await unit_of_work.flush()

        return ContentMapper.to_dto(restored)
