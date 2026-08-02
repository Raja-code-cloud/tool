"""Process startup initialization for the composition root."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import cast

from fastapi import FastAPI
from sqlalchemy import text

from cloud_content_hub.bootstrap.container import Container
from cloud_content_hub.bootstrap.shutdown import shutdown_application
from cloud_content_hub.core.logging import get_logger


@asynccontextmanager
async def bootstrap_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """FastAPI lifespan hook that runs bootstrap startup and shutdown."""

    container = cast(Container, app.state.container)
    await startup_application(container)
    get_logger().info("service.started", message="API service started")
    try:
        yield
    finally:
        await shutdown_application(container)
        get_logger().info("service.stopped", message="API service stopped")


async def startup_application(container: Container) -> None:
    """Initialize external dependencies and validate reachability before accepting work."""

    logger = get_logger()
    logger.info("bootstrap.startup.begin", message="Starting application dependencies")

    async with container.database_engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    logger.info("bootstrap.startup.database", message="Database connectivity verified")

    await container.redis.ping()
    logger.info("bootstrap.startup.redis", message="Redis connectivity verified")

    storage_health = await container.storage_provider.health_check()
    logger.info(
        "bootstrap.startup.storage",
        message="Storage provider initialized",
        healthy=storage_health.healthy,
    )

    for provider in container.ai_client.providers:
        health = await provider.health_check()
        logger.info(
            "bootstrap.startup.ai_provider",
            message="AI provider checked",
            provider=provider.name,
            healthy=health.healthy,
        )

    identity_report = await container.identity_health.check_all()
    logger.info(
        "bootstrap.startup.identity",
        message="Identity providers checked",
        healthy=identity_report.healthy,
        provider_count=len(identity_report.providers),
    )

    aggregate = await container.health_checker.check()
    logger.info(
        "bootstrap.startup.health",
        message="Health contributors registered",
        status=aggregate.status.value,
        check_count=len(aggregate.checks),
    )

    logger.info("bootstrap.startup.complete", message="Application startup complete")
