"""End-to-end video upload workflow tests."""

from __future__ import annotations

import pytest

from cloud_content_hub.application.assets.commands import UploadAssetCommand
from cloud_content_hub.application.assets.dto.requests import UploadAssetRequestDto
from cloud_content_hub.application.assets.queries import GetAssetQuery
from cloud_content_hub.application.shared.dto.base import OperationStatus
from cloud_content_hub.bootstrap.handlers import wire_handlers

from tests.e2e.conftest import WorkflowContext
from tests.fixtures.auth import workflow_actor
from tests.fixtures.constants import SAMPLE_MP4_BYTES

pytestmark = pytest.mark.e2e


@pytest.mark.asyncio
async def test_upload_video_queues_media_job(workflow_context: WorkflowContext) -> None:
    """Upload video → blob storage → thumbnail pipeline → metadata."""

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
                asset_type="video",
                title="Launch Video",
                filename="launch.mp4",
                content_type="video/mp4",
                content_length=len(SAMPLE_MP4_BYTES),
                file_data=SAMPLE_MP4_BYTES,
            ),
            idempotency_key="e2e-upload-video-0001",
        ),
    )

    assert operation.status == OperationStatus.QUEUED
    assert operation.resource_type == "asset"


@pytest.mark.asyncio
async def test_seeded_video_asset_exists(workflow_context: WorkflowContext) -> None:
    """Seeded video asset is retrievable from the asset repository."""

    registry = wire_handlers(workflow_context.container)
    handler = registry.resolve("get_asset")
    actor = workflow_actor(
        user_id=workflow_context.seed.user_id,
        workspace_id=workflow_context.seed.workspace_id,
    )
    asset = await handler.handle(
        actor,
        GetAssetQuery(asset_id=workflow_context.seed.video_asset_id),
    )

    assert asset.id == workflow_context.seed.video_asset_id
    assert asset.asset_type.value == "video"
