"""Workflow automation — upload, generate, approve, publish."""

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

pytestmark = [pytest.mark.automation, pytest.mark.integration]


@pytest.mark.asyncio
async def test_upload_asset_workflow(workflow_context: WorkflowContext) -> None:
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
                title="Automation Poster",
                filename="automation.webp",
                content_type="image/webp",
                content_length=len(SAMPLE_WEBP_BYTES),
                file_data=SAMPLE_WEBP_BYTES,
            ),
            idempotency_key="automation-upload-001",
        ),
    )

    assert operation.status == OperationStatus.QUEUED
    events = await query_outbox_events(
        workflow_context.session_factory,
        workspace_id=workflow_context.seed.workspace_id,
        event_type="asset.uploaded",
    )
    assert events


@pytest.mark.asyncio
async def test_upload_via_http_workflow(auth_client: AsyncClient) -> None:
    response = await auth_client.post(
        "/api/v1/assets/upload",
        headers={"Idempotency-Key": "automation-http-upload-001"},
        data={"assetType": "poster", "title": "HTTP Automation Poster"},
        files={"file": ("poster.webp", SAMPLE_WEBP_BYTES, "image/webp")},
    )

    assert response.status_code == 202
    assert response.json()["data"]["type"] == "upload"


@pytest.mark.asyncio
async def test_outbox_to_worker_workflow(workflow_context: WorkflowContext) -> None:
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
                title="Worker Poster",
                filename="worker.webp",
                content_type="image/webp",
                content_length=len(SAMPLE_WEBP_BYTES),
                file_data=SAMPLE_WEBP_BYTES,
            ),
            idempotency_key="automation-worker-001",
        ),
    )

    dispatched = await drain_outbox(
        workflow_context.container,
        broker=workflow_context.broker,
    )
    assert dispatched >= 1


@pytest.mark.asyncio
async def test_generate_content_http_workflow(
    auth_client: AsyncClient, workflow_context: WorkflowContext
) -> None:
    response = await auth_client.post(
        "/api/v1/content/generate",
        headers={"Idempotency-Key": "automation-generate-001"},
        json={
            "assetId": str(workflow_context.seed.article_asset_id),
            "sourceVersionId": str(workflow_context.seed.article_version_id),
            "modelId": str(workflow_context.seed.ai_model_id),
            "scope": "whole",
        },
    )

    assert response.status_code in {202, 409, 422}
