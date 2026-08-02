"""Shared fixtures for security regression tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from cloud_content_hub.api.dependencies import HandlerRegistry
from cloud_content_hub.bootstrap.api import create_app
from cloud_content_hub.core.config import Environment, Settings
from cloud_content_hub.infrastructure.identity.testing.fixtures import identity_factory


@pytest.fixture
def security_client() -> TestClient:
    app = create_app(Settings(environment=Environment.TEST))
    app.state.handlers = HandlerRegistry(handlers={})
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def jwt_service():
    return identity_factory().jwt_service
