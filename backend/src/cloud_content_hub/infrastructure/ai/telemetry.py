"""Metadata-only telemetry; content and secrets are never accepted."""

from collections.abc import Mapping

import structlog

from cloud_content_hub.infrastructure.ai.models import TokenUsage

logger = structlog.get_logger(__name__)

_SENSITIVE = frozenset(
    {
        "prompt",
        "content",
        "messages",
        "api_key",
        "authorization",
        "raw",
        "system",
        "user",
        "secret",
        "password",
        "token",
    }
)


def safe_metadata(values: Mapping[str, object]) -> dict[str, object]:
    return {
        key: value
        for key, value in values.items()
        if key.lower() not in _SENSITIVE and not key.lower().endswith("_key")
    }


def log_completion(
    *,
    provider: str,
    model: str,
    latency_ms: int,
    usage: TokenUsage,
    success: bool = True,
    retries: int = 0,
    request_id: str | None = None,
    correlation_id: str | None = None,
    estimated_cost: str | None = None,
) -> None:
    payload = safe_metadata(
        {
            "provider": provider,
            "model": model,
            "latency_ms": latency_ms,
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "total_tokens": usage.total_tokens,
            "success": success,
            "retries": retries,
            "request_id": request_id,
            "correlation_id": correlation_id,
            "estimated_cost": estimated_cost,
        }
    )
    event = "ai.completion.succeeded" if success else "ai.completion.failed"
    logger.info(event, **payload)


def log_stream_event(
    *,
    provider: str,
    model: str,
    success: bool = True,
    request_id: str | None = None,
    correlation_id: str | None = None,
) -> None:
    payload = safe_metadata(
        {
            "provider": provider,
            "model": model,
            "success": success,
            "request_id": request_id,
            "correlation_id": correlation_id,
        }
    )
    event = "ai.stream.succeeded" if success else "ai.stream.failed"
    logger.info(event, **payload)
