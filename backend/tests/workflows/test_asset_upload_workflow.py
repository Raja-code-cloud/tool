"""End-to-end asset upload workflow tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from cloud_content_hub.application.assets.commands import UploadAssetCommand
from cloud_content_hub.application.assets.dto.requests import UploadAssetRequestDto
from cloud_content_hub.application.shared.dto.base import OperationStatus
from cloud_content_hub.bootstrap.handlers import wire_handlers

from tests.e2e.conftest import WorkflowContext
from tests.fixtures.auth import workflow_actor
from tests.fixtures.constants import SAMPLE_WEBP_BYTES
from tests.fixtures.outbox import drain_outbox, query_outbox_events

pytestmark = pytest.mark.e2e


@pytest.mark.asyncio
async def test_upload_poster_queues_job_and_publishes_event(workflow_context: WorkflowContext) -> None:
    """Upload poster → metadata extraction → asset repository → outbox event."""

    registry = wire_handlers(workflow_context.container)
    handler = registry.resolve("upload_asset")
    actor = workflow_actor(
        user_id=workflow_context.seed.user_id,
        workspace_id=workflow_context.seed.workspace_id,
    )
    operation = await handler.handle(
        actor,
        UploadAssetCommand(
            request=UploadAssetRequestDto(
                asset_type="poster",
                title="Campaign Poster",
                filename="poster.webp",
                content_type="image/webp",
                content_length=len(SAMPLE_WEBP_BYTES),
                file_data=SAMPLE_WEBP_BYTES,
            ),
            idempotency_key="e2e-upload-poster-0001",
        ),
    )

    assert operation.status == OperationStatus.QUEUED
    assert operation.resource_id is not None

    events = await query_outbox_events(
        workflow_context.session_factory,
        workspace_id=workflow_context.seed.workspace_id,
        event_type="asset.uploaded",
    )
    assert len(events) >= 1
    assert events[-1].aggregate_type == "asset"


@pytest.mark.asyncio
async def test_upload_poster_via_http_returns_accepted(auth_client: AsyncClient) -> None:
    """HTTP upload endpoint accepts poster payloads."""

    response = await auth_client.post(
        "/api/v1/assets/upload",
        headers={"Idempotency-Key": "e2e-http-upload-poster"},
        data={"assetType": "poster", "title": "HTTP Poster"},
        files={"file": ("poster.webp", SAMPLE_WEBP_BYTES, "image/webp")},
    )

    assert response.status_code == 202
    body = response.json()
    assert body["success"] is True
    assert body["data"]["type"] == "upload"


@pytest.mark.asyncio
async def test_upload_poster_drains_outbox_to_celery(workflow_context: WorkflowContext) -> None:
    """Asset upload events are dispatched to the Celery broker via outbox."""

    registry = wire_handlers(workflow_context.container)
    handler = registry.resolve("upload_asset")
    actor = workflow_actor(
        user_id=workflow_context.seed.user_id,
        workspace_id=workflow_context.seed.workspace_id,
    )
    await handler.handle(
        actor,
        UploadAssetCommand(
            request=UploadAssetRequestDto(
                asset_type="poster",
                title="Outbox Poster",
                filename="outbox.webp",
                content_type="image/webp",
                content_length=len(SAMPLE_WEBP_BYTES),
                file_data=SAMPLE_WEBP_BYTES,
            ),
            idempotency_key="e2e-upload-outbox-0001",
        ),
    )

    dispatched = await drain_outbox(
        workflow_context.container,
        broker=workflow_context.broker,
    )

    assert dispatched >= 1
    assert any(task["queue"] == "media" for task in workflow_context.broker.tasks)
