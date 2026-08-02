import json
from collections.abc import AsyncGenerator
from types import TracebackType
from typing import Self, cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cloud_content_hub.api.pagination import decode_cursor, encode_cursor
from cloud_content_hub.api.routers.v1 import health as health_module
from cloud_content_hub.bootstrap.api import create_app
from cloud_content_hub.core import logging as logging_module
from cloud_content_hub.core.config import Environment, Settings
from cloud_content_hub.core.errors import (
    AuthenticationError,
    DependencyTimeoutError,
    ResourceNotFoundError,
    VersionConflictError,
)
from cloud_content_hub.infrastructure.database.session import session_scope


class FakeConnection:
    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
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


class TimeoutRecorder:
    def __init__(self, values: list[float]) -> None:
        self.values = values

    def __call__(self, seconds: float) -> "TimeoutRecorder":
        self.values.append(seconds)
        return self

    async def __aenter__(self) -> None:
        return None

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None


class RequestBody(BaseModel):
    name: str


def test_liveness_does_not_require_dependencies() -> None:
    with TestClient(create_app(Settings(environment=Environment.TEST))) as client:
        response = client.get("/live")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["status"] == "live"


def test_health_endpoint_is_available() -> None:
    with TestClient(create_app(Settings(environment=Environment.TEST))) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["status"] == "healthy"


def test_openapi_and_swagger_are_available() -> None:
    with TestClient(create_app(Settings(environment=Environment.TEST))) as client:
        schema_response = client.get("/openapi.json")
        docs_response = client.get("/docs")
    assert schema_response.status_code == 200
    assert schema_response.json()["info"]["x-service-name"] == "cloud-content-hub"
    assert schema_response.json()["openapi"] == "3.1.0"
    assert docs_response.status_code == 200


def test_structured_logs_include_required_service_context(
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = Settings(environment=Environment.TEST, service_version="9.8.7")
    logging_module.configure_logging(settings)
    logging_module.get_logger().info("test.completed", message="Test completed")
    record = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert record["service"] == "cloud-content-hub"
    assert record["environment"] == "test"
    assert record["version"] == "9.8.7"


def test_request_and_correlation_ids_are_propagated() -> None:
    with TestClient(create_app(Settings(environment=Environment.TEST))) as client:
        response = client.get(
            "/live",
            headers={"X-Request-ID": "request-123", "X-Correlation-ID": "workflow-123"},
        )
    assert response.headers["X-Request-ID"] == "request-123"
    assert response.headers["X-Correlation-ID"] == "workflow-123"


def test_invalid_request_id_is_replaced() -> None:
    with TestClient(create_app(Settings(environment=Environment.TEST))) as client:
        response = client.get("/live", headers={"X-Request-ID": "not valid"})
    assert response.headers["X-Request-ID"] != "not valid"


def test_application_error_uses_problem_details() -> None:
    app = create_app(Settings(environment=Environment.TEST))
    router = APIRouter()

    @router.get("/missing")
    async def missing() -> None:
        raise ResourceNotFoundError()

    app.include_router(router)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/missing")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["error"]["code"] == "resource_not_found"
    assert response.json()["success"] is False
    assert response.json()["requestId"] == response.headers["X-Request-ID"]


@pytest.mark.parametrize(
    ("error", "status", "code"),
    [
        (AuthenticationError(), 401, "authentication_required"),
        (VersionConflictError(), 409, "version_conflict"),
        (DependencyTimeoutError(), 504, "dependency_timeout"),
    ],
)
def test_exception_defaults_map_to_stable_problems(
    error: Exception, status: int, code: str
) -> None:
    app = create_app(Settings(environment=Environment.TEST))
    router = APIRouter()

    @router.get("/failure")
    async def failure() -> None:
        raise error

    app.include_router(router)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/failure")
    assert response.status_code == status
    assert response.json()["error"]["code"] == code


def test_malformed_json_returns_bad_request() -> None:
    app = create_app(Settings(environment=Environment.TEST))
    router = APIRouter()

    @router.post("/payload")
    async def payload(body: RequestBody) -> RequestBody:
        return body

    app.include_router(router)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/payload",
            content='{"name":',
            headers={"Content-Type": "application/json"},
        )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_request"


def test_readiness_checks_dependencies_with_separate_timeouts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = Settings(
        environment=Environment.TEST,
        database_timeout_seconds=3,
        redis_timeout_seconds=7,
    )
    app = create_app(settings)
    fake_container = FakeContainer(settings)
    app.state.container = fake_container
    recorded_timeouts: list[float] = []
    timeout = TimeoutRecorder(recorded_timeouts)
    monkeypatch.setattr(health_module, "timeout_after", timeout)
    with TestClient(app) as client:
        response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ready"
    assert recorded_timeouts == [3, 7]


@pytest.mark.asyncio
async def test_session_scope_rolls_back_on_failure() -> None:
    session = MagicMock(spec=AsyncSession)
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.rollback = AsyncMock()
    factory = cast(async_sessionmaker[AsyncSession], MagicMock(return_value=session))
    scope = cast(AsyncGenerator[AsyncSession], session_scope(factory))
    assert await anext(scope) is session
    with pytest.raises(RuntimeError, match="failure"):
        await scope.athrow(RuntimeError("failure"))
    session.rollback.assert_awaited_once()


def test_cursor_round_trip_and_tamper_rejection() -> None:
    cursor = encode_cursor({"id": "abc", "sort": "2026-08-02T00:00:00Z"}, b"test-secret")
    assert decode_cursor(cursor, b"test-secret")["id"] == "abc"
    with pytest.raises(ValueError, match="Invalid cursor"):
        decode_cursor(cursor, b"wrong-secret")


def test_production_rejects_wildcard_cors() -> None:
    with pytest.raises(ValueError, match="cannot contain"):
        Settings(environment=Environment.PRODUCTION, http_allowed_origins=["*"])
