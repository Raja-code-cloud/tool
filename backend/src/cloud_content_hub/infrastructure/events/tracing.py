"""Trace and correlation propagation helpers for event envelopes."""

from __future__ import annotations

from cloud_content_hub.infrastructure.events.models import EventMetadata
from cloud_content_hub.infrastructure.observability.tracing import current_trace_ids, inject_context


def build_event_headers(*, metadata: EventMetadata) -> dict[str, str]:
    """Build JSON-serializable outbox headers including active trace context."""

    trace_id, span_id = current_trace_ids()
    headers: dict[str, str] = {
        "source": metadata.source,
        "content_type": metadata.content_type,
    }
    if metadata.correlation_id:
        headers["correlation_id"] = metadata.correlation_id
    if metadata.request_id:
        headers["request_id"] = metadata.request_id
    if trace_id:
        headers["trace_id"] = trace_id
    elif metadata.trace_id:
        headers["trace_id"] = metadata.trace_id
    if span_id:
        headers["span_id"] = span_id
    elif metadata.span_id:
        headers["span_id"] = metadata.span_id

    carrier: dict[str, str] = {}
    inject_context(carrier)
    for key in ("traceparent", "tracestate"):
        if key in carrier:
            headers[key] = carrier[key]
    return headers
