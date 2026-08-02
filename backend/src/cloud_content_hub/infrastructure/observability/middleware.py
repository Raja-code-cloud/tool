"""ASGI middleware for tracing, IDs, metrics, timing, and access logs."""

import re
import time
from uuid import uuid4

import structlog
from opentelemetry.trace import SpanKind, Tracer
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from cloud_content_hub.core.context import bind_request_context, clear_request_context

from .config import ObservabilityConfig
from .metrics import ObservabilityMetrics
from .tracing import extract_context, traced_operation
from .utils import safe_route_label

_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


class ObservabilityMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        config: ObservabilityConfig,
        metrics: ObservabilityMetrics,
        tracer: Tracer,
        logger: structlog.stdlib.BoundLogger,
    ) -> None:
        self._app = app
        self._config = config
        self._metrics = metrics
        self._tracer = tracer
        self._logger = logger

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return
        headers = _headers(scope)
        request_id = _safe_id(headers.get("x-request-id")) or str(uuid4())
        correlation_id = _safe_id(headers.get("x-correlation-id")) or request_id
        context_tokens = bind_request_context(request_id, correlation_id)
        method = str(scope.get("method", "UNKNOWN")).upper()
        started = time.perf_counter()
        status_code = 500
        self._metrics.http_in_flight.labels(method=method).inc()

        async def observed_send(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
                response_headers = list(message.get("headers", []))
                response_headers.extend(
                    [
                        (b"x-request-id", request_id.encode("ascii")),
                        (b"x-correlation-id", correlation_id.encode("ascii")),
                    ]
                )
                message["headers"] = response_headers
            await send(message)

        parent = extract_context(headers)
        try:
            with traced_operation(
                self._tracer,
                f"{method} request",
                kind=SpanKind.SERVER,
                attributes={"http.request.method": method},
                parent_context=parent,
            ) as span:
                await self._app(scope, receive, observed_send)
                route = safe_route_label(scope)
                span.set_attribute("http.route", route)
                span.set_attribute("http.response.status_code", status_code)
        finally:
            route = safe_route_label(scope)
            elapsed = time.perf_counter() - started
            self._metrics.http_in_flight.labels(method=method).dec()
            self._metrics.http_requests.labels(
                method=method, route=route, status_class=f"{status_code // 100}xx"
            ).inc()
            self._metrics.http_duration.labels(method=method, route=route).observe(elapsed)
            if str(scope.get("path", "")) not in self._config.excluded_http_paths:
                self._logger.info(
                    "http.request.completed",
                    message="HTTP request completed",
                    method=method,
                    route=route,
                    status=status_code,
                    outcome=_outcome(status_code),
                    duration_ms=round(elapsed * 1000, 2),
                    performance="slow"
                    if elapsed >= self._config.slow_request_seconds
                    else "normal",
                )
            clear_request_context(context_tokens)


def _headers(scope: Scope) -> dict[str, str]:
    return {
        key.decode("latin-1").lower(): value.decode("latin-1")
        for key, value in scope.get("headers", [])
    }


def _safe_id(value: str | None) -> str | None:
    return value if value is not None and _ID_PATTERN.fullmatch(value) else None


def _outcome(status: int) -> str:
    if status < 400:
        return "success"
    if status < 500:
        return "client_error"
    return "server_error"
