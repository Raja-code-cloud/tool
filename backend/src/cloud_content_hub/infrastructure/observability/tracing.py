"""OpenTelemetry tracing, propagation, and operation helpers."""

from collections.abc import Iterator, Mapping, MutableMapping
from contextlib import contextmanager
from typing import Any

from opentelemetry import context, propagate, trace
from opentelemetry.context import Context
from opentelemetry.trace import Span, SpanKind, Status, StatusCode, Tracer

type Carrier = MutableMapping[str, str]


def inject_context(carrier: Carrier) -> None:
    """Inject W3C trace context into an HTTP/message carrier."""
    propagate.inject(carrier)


def extract_context(carrier: Mapping[str, str]) -> Context:
    """Extract W3C trace context from an untrusted carrier."""
    return propagate.extract(carrier)


def attach_context(carrier: Mapping[str, str]) -> Any:
    """Attach extracted context; caller must detach the returned token."""
    return context.attach(extract_context(carrier))


def detach_context(token: Any) -> None:
    context.detach(token)


def get_tracer(config_service_name: str, config_service_version: str) -> Tracer:
    """Return a tracer bound to the configured service identity."""
    return trace.get_tracer(config_service_name, config_service_version)


def current_trace_ids() -> tuple[str | None, str | None]:
    span_context = trace.get_current_span().get_span_context()
    if not span_context.is_valid:
        return None, None
    return f"{span_context.trace_id:032x}", f"{span_context.span_id:016x}"


@contextmanager
def traced_operation(
    tracer: Tracer,
    name: str,
    *,
    kind: SpanKind = SpanKind.INTERNAL,
    attributes: Mapping[str, str | int | float | bool] | None = None,
    parent_context: Context | None = None,
) -> Iterator[Span]:
    """Trace any HTTP, worker, DB, Redis, external, Azure, or AI operation."""
    with tracer.start_as_current_span(
        name,
        context=parent_context,
        kind=kind,
        attributes=dict(attributes or {}),
    ) as span:
        try:
            yield span
        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, type(error).__name__))
            raise


@contextmanager
def http_span(
    tracer: Tracer, name: str, attributes: Mapping[str, object] | None = None
) -> Iterator[Span]:
    with traced_operation(
        tracer, name, kind=SpanKind.SERVER, attributes=_attributes(attributes)
    ) as span:
        yield span


@contextmanager
def background_span(
    tracer: Tracer, name: str, attributes: Mapping[str, object] | None = None
) -> Iterator[Span]:
    with traced_operation(
        tracer, name, kind=SpanKind.CONSUMER, attributes=_attributes(attributes)
    ) as span:
        yield span


@contextmanager
def client_span(
    tracer: Tracer, name: str, attributes: Mapping[str, object] | None = None
) -> Iterator[Span]:
    """Create a client span for DB, Redis, HTTP, Azure, or AI calls."""
    with traced_operation(
        tracer, name, kind=SpanKind.CLIENT, attributes=_attributes(attributes)
    ) as span:
        yield span


def _attributes(values: Mapping[str, object] | None) -> dict[str, str | int | float | bool]:
    return {
        key: value
        for key, value in (values or {}).items()
        if isinstance(value, (str, int, float, bool))
    }
