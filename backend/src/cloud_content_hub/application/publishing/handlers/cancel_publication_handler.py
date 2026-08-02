"""Cancel publication command handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.publishing.commands import CancelPublicationCommand
from cloud_content_hub.application.publishing.dto.responses import PublicationDto
from cloud_content_hub.application.publishing.exceptions.publishing_errors import (
    PublicationNotFoundError,
)
from cloud_content_hub.application.publishing.interfaces.publication_repository import (
    IPublicationRepository,
    PublicationStatus,
)
from cloud_content_hub.application.publishing.mappers.publication_mapper import PublicationMapper
from cloud_content_hub.application.publishing.validators.publication_validator import (
    validate_cancellation,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.core.errors import VersionConflictError


class CancelPublicationHandler:
    """Orchestrates publication cancellation."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        publication_repository_factory: Callable[[IUnitOfWork], IPublicationRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._publication_repository_factory = publication_repository_factory

    async def handle(
        self, actor: ActorContext, command: CancelPublicationCommand
    ) -> PublicationDto:
        require_permission(actor, "publishing:delete")

        async with self._unit_of_work_factory() as unit_of_work:
            publication_repository = self._publication_repository_factory(unit_of_work)
            publication = await publication_repository.get_by_id(
                workspace_id=actor.workspace_id,
                publication_id=command.publication_id,
            )
            if publication is None:
                raise PublicationNotFoundError(
                    parameters={"publicationId": str(command.publication_id)}
                )
            if publication.status == PublicationStatus.CANCELLED:
                return PublicationMapper.to_dto(publication)
            if publication.version != command.expected_version:
                raise VersionConflictError(
                    parameters={
                        "publicationId": str(command.publication_id),
                        "expectedVersion": command.expected_version,
                    },
                )

            validate_cancellation(publication)
            updated = await publication_repository.update_status(
                workspace_id=actor.workspace_id,
                publication_id=command.publication_id,
                status=PublicationStatus.CANCELLED,
                expected_version=command.expected_version,
                updated_by=actor.user_id,
            )
            await unit_of_work.flush()

        return PublicationMapper.to_dto(updated)
