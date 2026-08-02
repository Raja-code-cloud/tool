"""Archive content command handler."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from cloud_content_hub.application.content.commands import ArchiveContentCommand
from cloud_content_hub.application.content.dto.responses import ContentDto
from cloud_content_hub.application.content.events import ContentArchived
from cloud_content_hub.application.content.interfaces.content_repository import (
    ContentLifecycleStatus,
    IContentRepository,
)
from cloud_content_hub.application.content.interfaces.event_publisher import IContentEventPublisher
from cloud_content_hub.application.content.mappers.content_mapper import ContentMapper
from cloud_content_hub.application.content.validators.content_validator import (
    validate_archive,
    validate_expected_version,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class ArchiveContentHandler:
    """Orchestrates content archival."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        content_repository_factory: Callable[[IUnitOfWork], IContentRepository],
        event_publisher_factory: Callable[[IUnitOfWork], IContentEventPublisher],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._content_repository_factory = content_repository_factory
        self._event_publisher_factory = event_publisher_factory

    async def handle(self, actor: ActorContext, command: ArchiveContentCommand) -> ContentDto:
        require_permission(actor, "content:write")

        async with self._unit_of_work_factory() as unit_of_work:
            content_repository = self._content_repository_factory(unit_of_work)
            event_publisher = self._event_publisher_factory(unit_of_work)

            content = await content_repository.get_by_id(
                workspace_id=actor.workspace_id,
                content_id=command.content_id,
            )
            content = validate_archive(content)
            assert content is not None
            validate_expected_version(content, command.expected_version)

            if content.lifecycle_status == ContentLifecycleStatus.ARCHIVED:
                return ContentMapper.to_dto(content)

            updated = await content_repository.update_lifecycle_status(
                workspace_id=actor.workspace_id,
                content_id=command.content_id,
                lifecycle_status=ContentLifecycleStatus.ARCHIVED,
                expected_version=command.expected_version,
                updated_by=actor.user_id,
            )
            await event_publisher.publish(
                ContentArchived(
                    workspace_id=actor.workspace_id,
                    content_id=command.content_id,
                    actor_id=actor.user_id,
                    version=updated.version,
                    occurred_at=datetime.now(UTC),
                ),
                unit_of_work=unit_of_work,
            )
            await unit_of_work.flush()

        return ContentMapper.to_dto(updated)
