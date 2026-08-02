from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Protocol, cast

from fastapi import FastAPI

from cloud_content_hub.core.logging import get_logger


class ClosableContainer(Protocol):
    async def close(self) -> None: ...


@asynccontextmanager
async def application_lifespan(app: FastAPI) -> AsyncIterator[None]:
    get_logger().info("service.started", message="API service started")
    try:
        yield
    finally:
        container = cast(ClosableContainer, app.state.container)
        await container.close()
        get_logger().info("service.stopped", message="API service stopped")
