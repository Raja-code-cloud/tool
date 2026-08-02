"""Reject content command handler."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from cloud_content_hub.application.content.commands import RejectContentCommand
from cloud_content_hub.application.content.dto.responses import GenerationOutputDto
from cloud_content_hub.application.content.events import ContentRejected
from cloud_content_hub.application.content.interfaces.content_repository import (
    IContentRepository,
    IGenerationOutputRepository,
)
from cloud_content_hub.application.content.interfaces.event_publisher import IContentEventPublisher
from cloud_content_hub.application.content.mappers.content_mapper import ContentMapper
from cloud_content_hub.application.content.validators.content_validator import (
    validate_expected_version,
    validate_rejection,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class RejectContentHandler:
    """Orchestrates generation output rejection."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        content_repository_factory: Callable[[IUnitOfWork], IContentRepository],
        generation_output_repository_factory: Callable[[IUnitOfWork], IGenerationOutputRepository],
        event_publisher_factory: Callable[[IUnitOfWork], IContentEventPublisher],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._content_repository_factory = content_repository_factory
        self._generation_output_repository_factory = generation_output_repository_factory
        self._event_publisher_factory = event_publisher_factory

    async def handle(
        self, actor: ActorContext, command: RejectContentCommand
    ) -> GenerationOutputDto:
        require_permission(actor, "content:write")

        async with self._unit_of_work_factory() as unit_of_work:
            content_repository = self._content_repository_factory(unit_of_work)
            output_repository = self._generation_output_repository_factory(unit_of_work)
            event_publisher = self._event_publisher_factory(unit_of_work)

            content = await content_repository.get_by_id(
                workspace_id=actor.workspace_id,
                content_id=command.content_id,
            )
            output = await output_repository.get_by_id(
                workspace_id=actor.workspace_id,
                output_id=command.request.output_id,
            )
            content, output = validate_rejection(content, output)
            assert content is not None
            validate_expected_version(content, command.expected_version)

            rejected = await output_repository.reject(
                workspace_id=actor.workspace_id,
                output_id=output.id,
                updated_by=actor.user_id,
                reason=command.request.reason,
            )
            await event_publisher.publish(
                ContentRejected(
                    workspace_id=actor.workspace_id,
                    content_id=content.id,
                    output_id=output.id,
                    actor_id=actor.user_id,
                    reason=command.request.reason,
                    occurred_at=datetime.now(UTC),
                ),
                unit_of_work=unit_of_work,
            )
            await unit_of_work.flush()

        return ContentMapper.to_generation_output_dto(rejected)
