"""Scheduler API automation tests."""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient

from tests.fixtures.app import bound_principal, workspace_headers

pytestmark = pytest.mark.api


@pytest.mark.asyncio
async def test_create_schedule(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.post(
            "/api/v1/schedule",
            headers=workspace_headers(extra={"Idempotency-Key": "api-schedule-001"}),
            json={
                "publicationTargetId": str(uuid4()),
                "requestedLocalAt": "2026-08-03T09:00:00",
                "timeZone": "UTC",
            },
        )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_list_schedules(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get("/api/v1/schedule", headers=workspace_headers())

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_schedule(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            f"/api/v1/schedule/{uuid4()}",
            headers=workspace_headers(),
        )

    assert response.status_code == 200
