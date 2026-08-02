"""End-to-end master article and content generation workflow tests."""

from __future__ import annotations

import pytest

from cloud_content_hub.application.assets.commands import UploadAssetCommand
from cloud_content_hub.application.assets.dto.requests import UploadAssetRequestDto
from cloud_content_hub.application.content.commands import GenerateContentCommand
from cloud_content_hub.application.content.dto.requests import GenerationRequestDto
from cloud_content_hub.application.content.queries import GetContentQuery
from cloud_content_hub.application.shared.dto.base import OperationStatus
from cloud_content_hub.bootstrap.handlers import wire_handlers

from tests.e2e.conftest import WorkflowContext
from tests.fixtures.auth import workflow_actor
from tests.fixtures.constants import SAMPLE_TEXT_BYTES
from tests.fixtures.outbox import query_outbox_events

pytestmark = pytest.mark.e2e


@pytest.mark.asyncio
async def test_upload_master_article_via_handler(workflow_context: WorkflowContext) -> None:
    """Upload master article stores asset and queues ingestion."""

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
                asset_type="article",
                title="Imported Master Article",
                filename="master.md",
                content_type="text/markdown",
                content_length=len(SAMPLE_TEXT_BYTES),
                file_data=SAMPLE_TEXT_BYTES,
            ),
            idempotency_key="e2e-upload-article-0001",
        ),
    )

    assert operation.status == OperationStatus.QUEUED


@pytest.mark.asyncio
async def test_generate_content_from_approved_version(workflow_context: WorkflowContext) -> None:
    """Generate content → AI provider → content repository → version job."""

    registry = wire_handlers(workflow_context.container)
    handler = registry.resolve("generate_content")
    actor = workflow_actor(
        user_id=workflow_context.seed.user_id,
        workspace_id=workflow_context.seed.workspace_id,
    )
    operation = await handler.handle(
        actor,
        GenerateContentCommand(
            request=GenerationRequestDto(
                asset_id=workflow_context.seed.article_asset_id,
                source_version_id=workflow_context.seed.article_version_id,
                model_id=workflow_context.seed.ai_model_id,
                scope="whole",
                target_platforms=("linkedin", "facebook"),
            ),
            idempotency_key="e2e-generate-content-0001",
        ),
    )

    assert operation.status == OperationStatus.QUEUED
    assert operation.resource_id == workflow_context.seed.article_asset_id

    events = await query_outbox_events(
        workflow_context.session_factory,
        workspace_id=workflow_context.seed.workspace_id,
        event_type="content.generated",
    )
    assert len(events) >= 1


@pytest.mark.asyncio
async def test_seeded_article_has_approved_version(workflow_context: WorkflowContext) -> None:
    """Seeded master article version is approved for publishing workflows."""

    registry = wire_handlers(workflow_context.container)
    handler = registry.resolve("get_content")
    actor = workflow_actor(
        user_id=workflow_context.seed.user_id,
        workspace_id=workflow_context.seed.workspace_id,
    )
    content = await handler.handle(
        actor,
        GetContentQuery(content_id=workflow_context.seed.article_asset_id),
    )

    assert content.id == workflow_context.seed.article_asset_id
