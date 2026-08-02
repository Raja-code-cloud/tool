"""Publishing API automation tests."""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient

from tests.fixtures.app import bound_principal, workspace_headers

pytestmark = pytest.mark.api


@pytest.mark.asyncio
async def test_create_publication(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.post(
            "/api/v1/publish",
            headers=workspace_headers(extra={"Idempotency-Key": "api-publish-001"}),
            json={
                "contentId": str(uuid4()),
                "contentVersionId": str(uuid4()),
                "title": "API Publication",
                "targets": [{"socialAccountId": str(uuid4())}],
            },
        )

    assert response.status_code == 201
    assert response.headers["etag"]


@pytest.mark.asyncio
async def test_dispatch_publication(api_client: AsyncClient) -> None:
    publication_id = uuid4()
    async with bound_principal():
        response = await api_client.post(
            f"/api/v1/publish/{publication_id}",
            headers=workspace_headers(
                extra={"Idempotency-Key": "api-dispatch-001", "If-Match": "1"}
            ),
        )

    assert response.status_code == 202


@pytest.mark.asyncio
async def test_list_publication_history(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get("/api/v1/publish/history", headers=workspace_headers())

    assert response.status_code == 200
