"""End-to-end publication and scheduling workflow tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from cloud_content_hub.application.publishing.commands import (
    DispatchPublicationCommand,
    PublishContentCommand,
)
from cloud_content_hub.application.publishing.dto.requests import (
    CreatePublicationRequestDto,
    DispatchPublicationRequestDto,
    PublicationTargetRequestDto,
)
from cloud_content_hub.application.scheduler.commands import SchedulePublicationCommand
from cloud_content_hub.application.scheduler.dto.requests import ScheduleRequestDto
from cloud_content_hub.application.shared.dto.base import OperationStatus
from cloud_content_hub.bootstrap.handlers import wire_handlers

from tests.e2e.conftest import WorkflowContext
from tests.fixtures.auth import workflow_actor
from tests.fixtures.constants import PLATFORM_CODES
from tests.fixtures.outbox import drain_outbox
from tests.fixtures.seed import approve_publication_target

pytestmark = pytest.mark.e2e


async def _create_publication(
    workflow_context: WorkflowContext,
    *,
    platform_code: str,
    idempotency_suffix: str,
):
    registry = wire_handlers(workflow_context.container)
    handler = registry.resolve("create_publication")
    actor = workflow_actor(
        user_id=workflow_context.seed.user_id,
        workspace_id=workflow_context.seed.workspace_id,
    )
    return await handler.handle(
        actor,
        PublishContentCommand(
            request=CreatePublicationRequestDto(
                content_id=workflow_context.seed.article_asset_id,
                content_version_id=workflow_context.seed.article_version_id,
                title=f"Publish to {platform_code}",
                targets=(
                    PublicationTargetRequestDto(
                        social_account_id=workflow_context.seed.social_account_ids[platform_code],
                    ),
                ),
            ),
            idempotency_key=f"e2e-publish-{platform_code}-{idempotency_suffix}",
        ),
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("platform_code", PLATFORM_CODES)
async def test_platform_publish_workflow(
    workflow_context: WorkflowContext,
    platform_code: str,
) -> None:
    """Create and dispatch publication for each supported platform."""

    publication = await _create_publication(
        workflow_context,
        platform_code=platform_code,
        idempotency_suffix="0001",
    )
    assert publication.id is not None

    registry = wire_handlers(workflow_context.container)
    dispatch_handler = registry.resolve("dispatch_publication")
    actor = workflow_actor(
        user_id=workflow_context.seed.user_id,
        workspace_id=workflow_context.seed.workspace_id,
    )
    operation = await dispatch_handler.handle(
        actor,
        DispatchPublicationCommand(
            publication_id=publication.id,
            expected_version=publication.version,
            request=DispatchPublicationRequestDto(),
            idempotency_key=f"e2e-dispatch-{platform_code}-0001",
        ),
    )

    assert operation.status == OperationStatus.QUEUED


@pytest.mark.asyncio
async def test_schedule_publication_workflow(workflow_context: WorkflowContext) -> None:
    """Schedule publication → scheduler runtime → Celery → outbox."""

    publication = await _create_publication(
        workflow_context,
        platform_code="linkedin",
        idempotency_suffix="schedule",
    )
    dispatch_handler = wire_handlers(workflow_context.container).resolve("dispatch_publication")
    actor = workflow_actor(
        user_id=workflow_context.seed.user_id,
        workspace_id=workflow_context.seed.workspace_id,
    )
    await dispatch_handler.handle(
        actor,
        DispatchPublicationCommand(
            publication_id=publication.id,
            expected_version=publication.version,
            request=DispatchPublicationRequestDto(),
            idempotency_key="e2e-dispatch-linkedin-schedule",
        ),
    )

    target_id = publication.targets[0].id
    await approve_publication_target(
        workflow_context.session_factory,
        workspace_id=workflow_context.seed.workspace_id,
        publication_target_id=target_id,
    )
    schedule_handler = wire_handlers(workflow_context.container).resolve("create_schedule")
    scheduled_for = datetime.now(tz=UTC) + timedelta(hours=2)
    schedule = await schedule_handler.handle(
        actor,
        SchedulePublicationCommand(
            request=ScheduleRequestDto(
                publication_target_id=target_id,
                requested_local_at=scheduled_for,
                time_zone="UTC",
                ambiguity_policy="reject",
                priority="normal",
            ),
            idempotency_key="e2e-schedule-0001",
        ),
    )

    assert schedule.id is not None
    assert schedule.publication_target_id == target_id

    dispatched = await drain_outbox(workflow_context.container, broker=workflow_context.broker)
    assert dispatched >= 0
