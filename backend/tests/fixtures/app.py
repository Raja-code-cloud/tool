"""FastAPI test application factory for API and regression suites."""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from cloud_content_hub.api.dependencies import HandlerRegistry
from cloud_content_hub.api.errors import install_exception_handlers
from cloud_content_hub.api.routers.v1.router import root_router
from cloud_content_hub.infrastructure.identity.middleware import bind_principal, clear_principal
from cloud_content_hub.infrastructure.identity.principal import Principal

from tests.fixtures.constants import WORKFLOW_PERMISSIONS
from tests.fixtures.factories import DEFAULT_USER_ID, DEFAULT_WORKSPACE_ID
from tests.fixtures.handlers import build_mock_handlers

DEFAULT_PERMISSIONS = WORKFLOW_PERMISSIONS


def build_principal(*, permissions: frozenset[str] = DEFAULT_PERMISSIONS) -> Principal:
    """Build a mock authenticated principal for handler-layer tests."""

    return Principal(
        subject=str(DEFAULT_USER_ID),
        provider="mock",
        authenticated=True,
        permissions=permissions,
    )


def create_api_test_app(handlers: Mapping[str, Any] | None = None) -> FastAPI:
    """Create a minimal FastAPI app wired with mocked handlers."""

    app = FastAPI(title="api-test")
    container = MagicMock()
    container.settings.service_version = "1.0.0-regression"
    app.state.container = container
    app.state.handlers = HandlerRegistry(handlers=dict(handlers or build_mock_handlers()))
    install_exception_handlers(app)
    app.include_router(root_router)
    return app


def workspace_headers(
    *,
    workspace_id: UUID = DEFAULT_WORKSPACE_ID,
    token: str = "regression-test-token",
    extra: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Build authenticated workspace-scoped request headers."""

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Workspace-ID": str(workspace_id),
    }
    if extra:
        headers.update(extra)
    return headers


@asynccontextmanager
async def bound_principal(*, permissions: frozenset[str] = DEFAULT_PERMISSIONS) -> AsyncIterator[None]:
    """Bind a principal for the duration of an HTTP request."""

    token = bind_principal(build_principal(permissions=permissions))
    try:
        yield
    finally:
        clear_principal(token)


@pytest.fixture
def mock_handlers() -> dict[str, Any]:
    return build_mock_handlers()


@pytest.fixture
def api_app(mock_handlers: dict[str, Any]) -> FastAPI:
    return create_api_test_app(mock_handlers)


@pytest.fixture
async def api_client(api_app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=api_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def headers() -> dict[str, str]:
    return workspace_headers()
