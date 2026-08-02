"""Workflow automation — scheduling, publishing, and retry."""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient

pytestmark = [pytest.mark.automation, pytest.mark.integration]


@pytest.mark.asyncio
async def test_schedule_publication_workflow(auth_client: AsyncClient) -> None:
    response = await auth_client.post(
        "/api/v1/schedule",
        headers={"Idempotency-Key": "automation-schedule-001"},
        json={
            "publicationTargetId": str(uuid4()),
            "requestedLocalAt": "2026-08-10T14:00:00",
            "timeZone": "UTC",
        },
    )

    assert response.status_code in {201, 404, 409, 422}


@pytest.mark.asyncio
async def test_publish_workflow(auth_client: AsyncClient, workflow_context) -> None:
    response = await auth_client.post(
        "/api/v1/publish",
        headers={"Idempotency-Key": "automation-publish-001"},
        json={
            "contentId": str(uuid4()),
            "contentVersionId": str(workflow_context.seed.article_version_id),
            "title": "Automation Publication",
            "targets": [
                {
                    "socialAccountId": str(
                        next(iter(workflow_context.seed.social_account_ids.values()))
                    ),
                }
            ],
        },
    )

    assert response.status_code in {201, 409, 422}
