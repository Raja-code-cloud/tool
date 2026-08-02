"""Dispatch publication command handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.publishing.commands import DispatchPublicationCommand
from cloud_content_hub.application.publishing.exceptions.publishing_errors import (
    PublicationNotFoundError,
)
from cloud_content_hub.application.publishing.interfaces.publication_repository import (
    IPublicationRepository,
    PublicationStatus,
)
from cloud_content_hub.application.publishing.validators.publication_validator import (
    validate_dispatch,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.dto.base import OperationDto
from cloud_content_hub.application.shared.interfaces.job_queue import (
    IBackgroundJobRepository,
    JobQueueName,
    NewBackgroundJob,
)
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.application.shared.mappers.operation_mapper import map_publishing_operation
from cloud_content_hub.core.errors import IdempotencyConflictError, VersionConflictError


class DispatchPublicationHandler:
    """Orchestrates asynchronous publication dispatch."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        publication_repository_factory: Callable[[IUnitOfWork], IPublicationRepository],
        job_repository_factory: Callable[[IUnitOfWork], IBackgroundJobRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._publication_repository_factory = publication_repository_factory
        self._job_repository_factory = job_repository_factory

    async def handle(
        self, actor: ActorContext, command: DispatchPublicationCommand
    ) -> OperationDto:
        require_permission(actor, "publishing:write")

        async with self._unit_of_work_factory() as unit_of_work:
            job_repository = self._job_repository_factory(unit_of_work)
            existing = await job_repository.get_by_idempotency_key(
                workspace_id=actor.workspace_id,
                job_type="publication_dispatch",
                idempotency_key=command.idempotency_key,
            )
            if existing is not None:
                if existing.resource_id != command.publication_id:
                    raise IdempotencyConflictError(
                        detail="Idempotency key was reused with a different dispatch request.",
                    )
                return map_publishing_operation(existing)

            publication_repository = self._publication_repository_factory(unit_of_work)
            publication = await publication_repository.get_by_id(
                workspace_id=actor.workspace_id,
                publication_id=command.publication_id,
            )
            if publication is None:
                raise PublicationNotFoundError(
                    parameters={"publicationId": str(command.publication_id)}
                )
            if publication.version != command.expected_version:
                raise VersionConflictError(
                    parameters={
                        "publicationId": str(command.publication_id),
                        "expectedVersion": command.expected_version,
                    },
                )

            validate_dispatch(publication)
            await publication_repository.update_status(
                workspace_id=actor.workspace_id,
                publication_id=publication.id,
                status=PublicationStatus.IN_PROGRESS,
                expected_version=command.expected_version,
                updated_by=actor.user_id,
            )

            job = await job_repository.create(
                NewBackgroundJob(
                    workspace_id=actor.workspace_id,
                    job_type="publication_dispatch",
                    queue_name=JobQueueName.MAINTENANCE,
                    resource_type="publication",
                    resource_id=publication.id,
                    idempotency_key=command.idempotency_key,
                    created_by=actor.user_id,
                )
            )
            await unit_of_work.flush()

        return map_publishing_operation(job)
