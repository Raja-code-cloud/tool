"""Graceful shutdown for the composition root."""

from __future__ import annotations

from cloud_content_hub.bootstrap.container import Container
from cloud_content_hub.core.logging import get_logger


async def shutdown_application(container: Container) -> None:
    """Release process-scoped resources in reverse dependency order."""

    logger = get_logger()
    logger.info("bootstrap.shutdown.begin", message="Shutting down application dependencies")

    await container.storage_provider.close()

    for provider in container.ai_client.providers:
        close = getattr(provider, "close", None)
        if callable(close):
            result = close()
            if hasattr(result, "__await__"):
                await result

    await container.redis.aclose()
    await container.database_engine.dispose()

    logger.info("bootstrap.shutdown.complete", message="Application shutdown complete")
