"""Shared fixtures for pytest-benchmark suites."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import pytest
from httpx import AsyncClient

from tests.performance.conftest import (  # noqa: F401
    asset_dto,
    celery_broker,
    event_config,
    mock_handlers,
    operation_dto,
    perf_headers,
    principal_token,
    storage_provider,
    user_id,
    workspace_id,
)
from tests.performance.helpers.http import create_async_client, create_test_client

pytestmark = pytest.mark.benchmark


@pytest.fixture
async def benchmark_client(mock_handlers: dict[str, Any]) -> AsyncIterator[AsyncClient]:
    async for client in create_async_client(handlers=mock_handlers):
        yield client


@pytest.fixture
def sync_client() -> Any:
    return create_test_client()
