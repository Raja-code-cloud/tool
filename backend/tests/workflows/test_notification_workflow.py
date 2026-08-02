"""End-to-end notification delivery workflow tests."""

from __future__ import annotations

import pytest

from cloud_content_hub.application.notifications.dto.requests import NotificationRequestDto
from cloud_content_hub.workers.factory import create_worker_bundle
from tests.e2e.conftest import WorkflowContext
from tests.fixtures.auth import workflow_actor
from tests.fixtures.outbox import drain_outbox, query_outbox_events

pytestmark = pytest.mark.e2e


@pytest.mark.asyncio
async def test_notification_delivery_publishes_event(workflow_context: WorkflowContext) -> None:
    """Notification delivery → outbox event."""

    worker_bundle = create_worker_bundle(workflow_context.container)
    handler = worker_bundle.registry.get("cloud_content_hub.tasks.deliver_notification")
    actor = workflow_actor(
        user_id=workflow_context.seed.user_id,
        workspace_id=workflow_context.seed.workspace_id,
    )
    from cloud_content_hub.workers.base import WorkerTaskPayload

    notification = await handler(
        actor,
        WorkerTaskPayload(
            workspace_id=workflow_context.seed.workspace_id,
            actor_id=workflow_context.seed.user_id,
            job_id=workflow_context.seed.notification_type_id,
            command={
                "request": NotificationRequestDto(
                    recipient_user_id=workflow_context.seed.user_id,
                    type_code="content.approved",
                    title="Content approved",
                    body="Your content was approved for publishing.",
                    severity="info",
                ).model_dump(mode="json")
            },
        ),
    )

    assert notification.id is not None

    events = await query_outbox_events(
        workflow_context.session_factory,
        workspace_id=workflow_context.seed.workspace_id,
        event_type="notification.created",
    )
    assert len(events) >= 1


@pytest.mark.asyncio
async def test_notification_outbox_drains_to_celery(workflow_context: WorkflowContext) -> None:
    """Notification events drain through outbox to Celery."""

    worker_bundle = create_worker_bundle(workflow_context.container)
    handler = worker_bundle.registry.get("cloud_content_hub.tasks.deliver_notification")
    actor = workflow_actor(
        user_id=workflow_context.seed.user_id,
        workspace_id=workflow_context.seed.workspace_id,
    )
    from cloud_content_hub.workers.base import WorkerTaskPayload

    await handler(
        actor,
        WorkerTaskPayload(
            workspace_id=workflow_context.seed.workspace_id,
            actor_id=workflow_context.seed.user_id,
            job_id=workflow_context.seed.notification_type_id,
            command={
                "request": NotificationRequestDto(
                    recipient_user_id=workflow_context.seed.user_id,
                    type_code="content.approved",
                    title="Retry notification",
                    body="Notification retry path.",
                    severity="info",
                ).model_dump(mode="json")
            },
        ),
    )

    dispatched = await drain_outbox(workflow_context.container, broker=workflow_context.broker)
    assert dispatched >= 1


@pytest.mark.asyncio
async def test_list_notifications_via_http(auth_client) -> None:
    """Notification list endpoint is reachable for authenticated users."""

    response = await auth_client.get("/api/v1/notifications")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
