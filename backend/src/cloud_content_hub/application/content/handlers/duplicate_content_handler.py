"""Duplicate content command handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.content.commands import DuplicateContentCommand
from cloud_content_hub.application.content.dto.responses import ContentDto
from cloud_content_hub.application.content.interfaces.content_repository import (
    DuplicateContentInput,
    IContentRepository,
)
from cloud_content_hub.application.content.mappers.content_mapper import ContentMapper
from cloud_content_hub.application.content.validators.content_validator import validate_duplicate
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.job_queue import (
    IBackgroundJobRepository,
    JobQueueName,
    NewBackgroundJob,
)
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.core.errors import IdempotencyConflictError


class DuplicateContentHandler:
    """Orchestrates content duplication."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        content_repository_factory: Callable[[IUnitOfWork], IContentRepository],
        job_repository_factory: Callable[[IUnitOfWork], IBackgroundJobRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._content_repository_factory = content_repository_factory
        self._job_repository_factory = job_repository_factory

    async def handle(self, actor: ActorContext, command: DuplicateContentCommand) -> ContentDto:
        require_permission(actor, "content:write")

        async with self._unit_of_work_factory() as unit_of_work:
            job_repository = self._job_repository_factory(unit_of_work)
            existing = await job_repository.get_by_idempotency_key(
                workspace_id=actor.workspace_id,
                job_type="content_duplicate",
                idempotency_key=command.idempotency_key,
            )
            if existing is not None:
                if existing.resource_id is None:
                    raise IdempotencyConflictError(
                        detail="Idempotency key was reused with a different duplicate request.",
                    )
                content_repository = self._content_repository_factory(unit_of_work)
                duplicate = await content_repository.get_by_id(
                    workspace_id=actor.workspace_id,
                    content_id=existing.resource_id,
                )
                if duplicate is None:
                    raise IdempotencyConflictError(
                        detail="Idempotency key was reused with a different duplicate request.",
                    )
                return ContentMapper.to_dto(duplicate)

            content_repository = self._content_repository_factory(unit_of_work)
            source = await content_repository.get_by_id(
                workspace_id=actor.workspace_id,
                content_id=command.content_id,
            )
            validate_duplicate(source)
            assert source is not None

            duplicate = await content_repository.duplicate(
                DuplicateContentInput(
                    workspace_id=actor.workspace_id,
                    source_content_id=command.content_id,
                    title=command.request.title,
                    project_id=command.request.project_id,
                    folder_id=command.request.folder_id,
                    created_by=actor.user_id,
                )
            )
            await job_repository.create(
                NewBackgroundJob(
                    workspace_id=actor.workspace_id,
                    job_type="content_duplicate",
                    queue_name=JobQueueName.MAINTENANCE,
                    resource_type="content",
                    resource_id=duplicate.id,
                    idempotency_key=command.idempotency_key,
                    created_by=actor.user_id,
                )
            )
            await unit_of_work.flush()

        return ContentMapper.to_dto(duplicate)
