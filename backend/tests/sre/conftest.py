"""Shared fixtures for SRE validation tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from cloud_content_hub.bootstrap.api import create_app
from cloud_content_hub.core.config import Environment, Settings


class FakeConnection:
    async def __aenter__(self) -> FakeConnection:
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    async def execute(self, _statement: object) -> None:
        return None


class FakeEngine:
    def connect(self) -> FakeConnection:
        return FakeConnection()


class FakeRedis:
    async def ping(self) -> bool:
        return True


class FakeContainer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.database_engine = FakeEngine()
        self.redis = FakeRedis()

    async def close(self) -> None:
        return None


@pytest.fixture
def client() -> TestClient:
    settings = Settings(environment=Environment.TEST)
    app = create_app(settings)
    app.state.container = FakeContainer(settings)
    return TestClient(app)
