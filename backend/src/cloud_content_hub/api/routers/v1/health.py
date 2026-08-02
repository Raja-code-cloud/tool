"""Canonical unversioned health probes."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import cast

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from cloud_content_hub.api.responses import ProbeDto, success
from cloud_content_hub.api.schemas.transport import HealthDto
from cloud_content_hub.bootstrap.container import Container
from cloud_content_hub.core.errors import DependencyUnavailableError

router = APIRouter(tags=["Health"])
timeout_after = asyncio.timeout


@router.get("/health", operation_id="getHealth")
async def get_health(request: Request) -> JSONResponse:
    container = cast(Container, request.app.state.container)
    return JSONResponse(
        success(
            data=HealthDto(status="healthy", version=container.settings.service_version),
            message="Service health available.",
        ).model_dump(by_alias=True)
    )


@router.get("/live", operation_id="getLiveness")
async def get_liveness() -> JSONResponse:
    return JSONResponse(
        success(data=ProbeDto(status="live"), message="Service is live.").model_dump(by_alias=True)
    )


@router.get("/ready", operation_id="getReadiness")
async def get_readiness(request: Request) -> JSONResponse:
    container = cast(Container, request.app.state.container)
    checks: dict[str, str] = {}

    async def check_database() -> None:
        async with container.database_engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

    async def check_redis() -> None:
        await container.redis.ping()

    dependencies: tuple[tuple[str, Callable[[], Awaitable[None]], float], ...] = (
        ("database", check_database, container.settings.database_timeout_seconds),
        ("redis", check_redis, container.settings.redis_timeout_seconds),
    )
    for name, check, timeout_seconds in dependencies:
        try:
            async with timeout_after(timeout_seconds):
                await check()
            checks[name] = "ok"
        except Exception:
            checks[name] = "unavailable"

    ready = all(status == "ok" for status in checks.values())
    if not ready:
        raise DependencyUnavailableError(detail="Required dependencies are unavailable.")
    return JSONResponse(
        success(data=ProbeDto(status="ready"), message="Service is ready.").model_dump(
            by_alias=True
        )
    )
