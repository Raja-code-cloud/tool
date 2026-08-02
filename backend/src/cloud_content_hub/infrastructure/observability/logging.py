"""Structlog processors and safe operational logging helpers."""

import time
from collections.abc import AsyncIterator, Iterator, MutableMapping
from contextlib import asynccontextmanager, contextmanager
from types import TracebackType

import structlog

from cloud_content_hub.core.context import correlation_id_var, request_id_var

from .tracing import current_trace_ids
from .utils import redact_mapping

EventDict = MutableMapping[str, object]


def add_observability_context(
    _logger: object,
    _method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Enrich structlog events with request and active trace context."""
    if request_id := request_id_var.get():
        event_dict["request_id"] = request_id
    if correlation_id := correlation_id_var.get():
        event_dict["correlation_id"] = correlation_id
    trace_id, span_id = current_trace_ids()
    if trace_id:
        event_dict["trace_id"] = trace_id
    if span_id:
        event_dict["span_id"] = span_id
    return event_dict


def redact_event(
    _logger: object,
    _method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Redact known secret fields before JSON serialization."""
    return dict(redact_mapping(event_dict))


def format_exception(
    _logger: object,
    _method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Render exception metadata without serializing exception arguments."""
    exception = event_dict.pop("exception", None)
    if isinstance(exception, BaseException):
        event_dict["error_type"] = type(exception).__name__
        event_dict.setdefault("error_code", "unexpected_error")
    return event_dict


def observability_processors() -> tuple[structlog.types.Processor, ...]:
    """Processors to insert before the configured JSON renderer."""
    return add_observability_context, format_exception, redact_event


@contextmanager
def log_performance(
    logger: structlog.stdlib.BoundLogger,
    event: str,
    *,
    threshold_seconds: float = 0.0,
    **attributes: object,
) -> Iterator[None]:
    started = time.perf_counter()
    try:
        yield
    finally:
        duration = time.perf_counter() - started
        if duration >= threshold_seconds:
            logger.info(
                event,
                message="Operation completed",
                duration_ms=round(duration * 1000, 2),
                **dict(redact_mapping(attributes)),
            )


@asynccontextmanager
async def log_async_performance(
    logger: structlog.stdlib.BoundLogger,
    event: str,
    *,
    threshold_seconds: float = 0.0,
    **attributes: object,
) -> AsyncIterator[None]:
    with log_performance(
        logger, event, threshold_seconds=threshold_seconds, **attributes
    ):
        yield


def safe_exception_fields(
    exception_type: type[BaseException],
    traceback_type: type[TracebackType] | None = None,
) -> dict[str, str]:
    """Build safe exception fields for a boundary logger."""
    result = {"error_type": exception_type.__name__}
    if traceback_type is not None:
        result["traceback_type"] = traceback_type.__name__
    return result
