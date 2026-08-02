"""Workflow automation — analytics refresh and notification delivery."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.fixtures.app import analytics_period_params
from tests.fixtures.outbox import query_outbox_events

pytestmark = [pytest.mark.automation, pytest.mark.integration]


@pytest.mark.asyncio
async def test_analytics_refresh_workflow(auth_client: AsyncClient) -> None:
    dashboard = await auth_client.get(
        "/api/v1/analytics/dashboard",
        params=analytics_period_params(),
    )
    assert dashboard.status_code == 200
    assert "freshThrough" in dashboard.json()["data"]

    posts = await auth_client.get("/api/v1/analytics/posts")
    assert posts.status_code == 200


@pytest.mark.asyncio
async def test_notification_list_workflow(auth_client: AsyncClient) -> None:
    response = await auth_client.get("/api/v1/notifications")
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


@pytest.mark.asyncio
async def test_notification_events_in_outbox(workflow_context) -> None:
    events = await query_outbox_events(
        workflow_context.session_factory,
        workspace_id=workflow_context.seed.workspace_id,
    )
    assert isinstance(events, list)
