"""Critical-path regression pack — end-to-end business flows."""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient

from tests.fixtures.app import analytics_period_params, bound_principal, workspace_headers
from tests.fixtures.constants import SAMPLE_WEBP_BYTES

pytestmark = [pytest.mark.regression, pytest.mark.critical_path]


@pytest.mark.asyncio
async def test_upload_generate_publish_critical_path(api_client: AsyncClient) -> None:
    """Upload asset → generate content → create publication → dispatch."""

    headers = workspace_headers(extra={"Idempotency-Key": "critical-upload-001"})
    async with bound_principal():
        upload = await api_client.post(
            "/api/v1/assets/upload",
            headers=headers,
            data={"assetType": "poster", "title": "Critical Path Poster"},
            files={"file": ("poster.webp", SAMPLE_WEBP_BYTES, "image/webp")},
        )
        assert upload.status_code == 202
        asset_id = upload.json()["data"]["resourceId"]

        generate = await api_client.post(
            "/api/v1/content/generate",
            headers=workspace_headers(extra={"Idempotency-Key": "critical-generate-001"}),
            json={
                "assetId": asset_id,
                "sourceVersionId": str(uuid4()),
                "modelId": str(uuid4()),
                "scope": "whole",
            },
        )
        assert generate.status_code == 202

        content_version_id = str(uuid4())
        publication = await api_client.post(
            "/api/v1/publish",
            headers=workspace_headers(extra={"Idempotency-Key": "critical-publish-001"}),
            json={
                "contentId": str(uuid4()),
                "contentVersionId": content_version_id,
                "title": "Critical Publication",
                "targets": [{"socialAccountId": str(uuid4())}],
            },
        )
        assert publication.status_code == 201
        publication_id = publication.json()["data"]["id"]

        dispatch = await api_client.post(
            f"/api/v1/publish/{publication_id}",
            headers=workspace_headers(
                extra={"Idempotency-Key": "critical-dispatch-001", "If-Match": "1"}
            ),
        )
        assert dispatch.status_code == 202


@pytest.mark.asyncio
async def test_schedule_and_analytics_critical_path(api_client: AsyncClient) -> None:
    """Schedule publication and read analytics dashboard."""

    async with bound_principal():
        schedule = await api_client.post(
            "/api/v1/schedule",
            headers=workspace_headers(extra={"Idempotency-Key": "critical-schedule-001"}),
            json={
                "publicationTargetId": str(uuid4()),
                "requestedLocalAt": "2026-08-05T10:00:00",
                "timeZone": "UTC",
            },
        )
        assert schedule.status_code == 201

        dashboard = await api_client.get(
            "/api/v1/analytics/dashboard",
            headers=workspace_headers(),
            params=analytics_period_params(),
        )
        assert dashboard.status_code == 200
