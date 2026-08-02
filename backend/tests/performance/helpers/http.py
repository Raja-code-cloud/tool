"""HTTP client factories for performance and load validation."""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from typing import Any
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient

from cloud_content_hub.api.dependencies import HandlerRegistry
from cloud_content_hub.api.errors import install_exception_handlers
from cloud_content_hub.api.routers.v1.router import root_router
from cloud_content_hub.bootstrap.api import create_app
from cloud_content_hub.core.config import Environment, Settings
from cloud_content_hub.infrastructure.identity.middleware import bind_principal, clear_principal
from cloud_content_hub.infrastructure.identity.principal import Principal


DEFAULT_WORKSPACE_ID = UUID("01900000-0000-7000-8000-000000000001")
DEFAULT_USER_ID = UUID("01900000-0000-7000-8000-000000000010")


def build_principal(*, permissions: frozenset[str]) -> Principal:
    return Principal(
        subject=str(DEFAULT_USER_ID),
        provider="mock",
        authenticated=True,
        permissions=permissions,
    )


def auth_headers(
    *,
    workspace_id: UUID = DEFAULT_WORKSPACE_ID,
    extra: Mapping[str, str] | None = None,
) -> dict[str, str]:
    headers = {
        "Authorization": "Bearer perf-test-token",
        "X-Workspace-ID": str(workspace_id),
        "X-Correlation-ID": f"perf-{uuid4().hex[:12]}",
    }
    if extra:
        headers.update(extra)
    return headers


def create_mock_app(handlers: Mapping[str, Any]) -> FastAPI:
    """Build a minimal FastAPI app with mocked command/query handlers."""

    from unittest.mock import MagicMock

    app = FastAPI(title="performance-test")
    container = MagicMock()
    container.settings.service_version = "1.0.0-perf"
    app.state.container = container
    app.state.handlers = HandlerRegistry(handlers=dict(handlers))
    install_exception_handlers(app)
    app.include_router(root_router)
    return app


def create_test_client(*, handlers: Mapping[str, Any] | None = None) -> TestClient:
    """Create a synchronous TestClient for health and routing benchmarks."""

    if handlers is None:
        return TestClient(create_app(Settings(environment=Environment.TEST)))
    return TestClient(create_mock_app(handlers))


async def create_async_client(
    *,
    handlers: Mapping[str, Any],
) -> AsyncIterator[AsyncClient]:
    """Yield an async HTTP client bound to a mocked handler registry."""

    app = create_mock_app(handlers)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://perf.test") as client:
        yield client


def noop_handler(return_value: object | None = None) -> AsyncMock:
    handler = AsyncMock()
    handler.handle.return_value = return_value
    return handler
