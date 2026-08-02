"""Generate content command handler."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from cloud_content_hub.application.content.commands import GenerateContentCommand
from cloud_content_hub.application.content.events import ContentGenerated
from cloud_content_hub.application.content.exceptions.content_errors import (
    ContentVersionNotFoundError,
    GenerationValidationError,
)
from cloud_content_hub.application.content.interfaces.content_repository import (
    IContentRepository,
    IGenerationRequestRepository,
    NewGenerationRequest,
)
from cloud_content_hub.application.content.interfaces.event_publisher import IContentEventPublisher
from cloud_content_hub.application.content.validators.content_validator import (
    validate_generation_request,
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
from cloud_content_hub.application.shared.mappers.operation_mapper import map_generation_operation
from cloud_content_hub.core.errors import IdempotencyConflictError


class GenerateContentHandler:
    """Orchestrates AI content generation."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        content_repository_factory: Callable[[IUnitOfWork], IContentRepository],
        generation_repository_factory: Callable[[IUnitOfWork], IGenerationRequestRepository],
        job_repository_factory: Callable[[IUnitOfWork], IBackgroundJobRepository],
        event_publisher_factory: Callable[[IUnitOfWork], IContentEventPublisher],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._content_repository_factory = content_repository_factory
        self._generation_repository_factory = generation_repository_factory
        self._job_repository_factory = job_repository_factory
        self._event_publisher_factory = event_publisher_factory

    async def handle(self, actor: ActorContext, command: GenerateContentCommand) -> OperationDto:
        require_permission(actor, "content:generate")
        scope = validate_generation_request(command.request)

        async with self._unit_of_work_factory() as unit_of_work:
            job_repository = self._job_repository_factory(unit_of_work)
            existing = await job_repository.get_by_idempotency_key(
                workspace_id=actor.workspace_id,
                job_type="content_generation",
                idempotency_key=command.idempotency_key,
            )
            if existing is not None:
                if existing.resource_id != command.request.asset_id:
                    raise IdempotencyConflictError(
                        detail="Idempotency key was reused with a different generation request.",
                    )
                return map_generation_operation(existing)

            content_repository = self._content_repository_factory(unit_of_work)
            generation_repository = self._generation_repository_factory(unit_of_work)
            event_publisher = self._event_publisher_factory(unit_of_work)

            source_version = await content_repository.get_version_by_id(
                workspace_id=actor.workspace_id,
                version_id=command.request.source_version_id,
            )
            if source_version is None:
                raise ContentVersionNotFoundError(
                    parameters={"sourceVersionId": str(command.request.source_version_id)},
                )
            if source_version.asset_id != command.request.asset_id:
                raise GenerationValidationError(
                    detail="Source version does not belong to the asset."
                )

            model_enabled = await generation_repository.validate_model_enabled(
                workspace_id=actor.workspace_id,
                model_id=command.request.model_id,
            )
            if not model_enabled:
                raise GenerationValidationError(detail="The requested AI model is not enabled.")

            generation_id = await generation_repository.create(
                NewGenerationRequest(
                    workspace_id=actor.workspace_id,
                    asset_id=command.request.asset_id,
                    source_version_id=command.request.source_version_id,
                    model_id=command.request.model_id,
                    prompt_template_id=command.request.prompt_template_id,
                    brand_profile_id=command.request.brand_profile_id,
                    scope=scope,
                    parameters=dict(command.request.parameters),
                    selection_text=command.request.selection_text,
                    created_by=actor.user_id,
                    idempotency_key=command.idempotency_key,
                )
            )

            job = await job_repository.create(
                NewBackgroundJob(
                    workspace_id=actor.workspace_id,
                    job_type="content_generation",
                    queue_name=JobQueueName.AI,
                    resource_type="content",
                    resource_id=command.request.asset_id,
                    idempotency_key=command.idempotency_key,
                    created_by=actor.user_id,
                )
            )

            await event_publisher.publish(
                ContentGenerated(
                    workspace_id=actor.workspace_id,
                    content_id=command.request.asset_id,
                    asset_id=command.request.asset_id,
                    generation_request_id=generation_id,
                    actor_id=actor.user_id,
                    scope=scope.value,
                    occurred_at=datetime.now(UTC),
                ),
                unit_of_work=unit_of_work,
            )
            await unit_of_work.flush()

        return map_generation_operation(job)
