from unittest.mock import AsyncMock

import pytest
import structlog
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import SpanKind
from prometheus_client import generate_latest
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from cloud_content_hub.core.context import bind_request_context, clear_request_context
from cloud_content_hub.infrastructure.observability import (
    ApplicationHealthCheck,
    HealthChecker,
    HealthStatus,
    ObservabilityConfig,
    ObservabilityMiddleware,
    create_observability_bundle,
    create_ping_health_check,
    create_prometheus_app,
    create_registry,
    observability_processors,
)
from cloud_content_hub.infrastructure.observability.exporters import (
    AzureMonitorAlertSink,
    NoOpAlertSink,
    OTLPTracingExporter,
)
from cloud_content_hub.infrastructure.observability.health import PingHealthCheck
from cloud_content_hub.infrastructure.observability.logging import redact_event
from cloud_content_hub.infrastructure.observability.metrics import ObservabilityMetrics
from cloud_content_hub.infrastructure.observability.telemetry import InstrumentationHooks
from cloud_content_hub.infrastructure.observability.tracing import (
    attach_context,
    client_span,
    current_trace_ids,
    detach_context,
    inject_context,
    traced_operation,
)
from cloud_content_hub.infrastructure.observability.utils import redact_mapping, safe_route_label


@pytest.fixture
def config() -> ObservabilityConfig:
    return ObservabilityConfig(
        service_name="cloud-content-hub",
        service_version="0.1.0",
        environment="test",
    )


@pytest.fixture
def bundle(config: ObservabilityConfig):
    return create_observability_bundle(config)


def test_create_registry_is_isolated() -> None:
    first = create_registry()
    second = create_registry()
    metrics = ObservabilityMetrics.create(first)
    metrics.http_requests.labels(method="GET", route="/health", status_class="2xx").inc()
    body = generate_latest(second).decode("ascii")
    assert "http_requests_total" not in body


def test_metrics_factory_records_custom_counter(bundle) -> None:
    counter = bundle.metric_factory.counter("custom_events_total", "Custom events", ("kind",))
    counter.increment(labels={"kind": "demo"})
    body = generate_latest(bundle.registry).decode("ascii")
    assert "custom_events_total" in body


def test_instrumentation_hooks_record_worker_and_ai_signals(bundle) -> None:
    hooks = InstrumentationHooks(bundle.metrics)
    hooks.worker_job("media", "transcode", "success", 1.25)
    hooks.ai_request(
        "openai",
        "gpt-4",
        "generate",
        "success",
        duration_seconds=0.5,
        input_tokens=10,
        output_tokens=20,
    )
    hooks.blob_operation("azure", "upload", "success", bytes_transferred=512)
    hooks.auth_event("oidc", "success")
    hooks.cache_operation("redis", "get", "hit")
    hooks.database_operation("primary", "select", "success", duration_seconds=0.01)
    hooks.retry("storage", "upload", "timeout")
    body = generate_latest(bundle.registry).decode("ascii")
    assert "worker_jobs_total" in body
    assert "ai_requests_total" in body
    assert "blob_operations_total" in body
    assert "auth_events_total" in body
    assert "cache_operations_total" in body
    assert "database_operations_total" in body
    assert "retries_total" in body


def test_redact_mapping_removes_secret_fields() -> None:
    redacted = redact_mapping(
        {
            "request_id": "abc",
            "authorization": "Bearer secret",
            "api_key": "value",
            "count": 3,
        }
    )
    assert redacted["request_id"] == "abc"
    assert redacted["authorization"] == "[REDACTED]"
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["count"] == 3


def test_observability_processors_redact_and_add_trace_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer("test")
    tokens = bind_request_context("req-1", "corr-1")
    try:
        with tracer.start_as_current_span("test-span"):
            event_dict: dict[str, object] = {"event": "demo", "password": "secret"}
            for processor in observability_processors():
                event_dict = processor(None, "info", event_dict)
    finally:
        clear_request_context(tokens)
    assert event_dict["request_id"] == "req-1"
    assert event_dict["correlation_id"] == "corr-1"
    assert event_dict["trace_id"]
    assert event_dict["span_id"]
    assert event_dict["password"] == "[REDACTED]"


def test_redact_event_processor() -> None:
    event_dict = redact_event(None, "info", {"token": "abc", "route": "/health"})
    assert event_dict["token"] == "[REDACTED]"
    assert event_dict["route"] == "/health"


def test_safe_route_label_uses_template_or_unmatched() -> None:
    class FakeRoute:
        path = "/assets/{asset_id}"

    assert safe_route_label({"route": FakeRoute()}) == "/assets/{asset_id}"
    assert safe_route_label({}) == "unmatched"


@pytest.mark.asyncio
async def test_health_checker_aggregates_statuses() -> None:
    checker = HealthChecker(
        [
            ApplicationHealthCheck(),
            create_ping_health_check("database", AsyncMock(return_value=True)),
            create_ping_health_check(
                "redis", AsyncMock(return_value=False), degraded_on_failure=True
            ),
        ]
    )
    result = await checker.check()
    assert result.status is HealthStatus.DEGRADED
    assert len(result.checks) == 3


@pytest.mark.asyncio
async def test_ping_health_check_marks_unhealthy_on_exception() -> None:
    async def failing_ping() -> bool:
        raise RuntimeError("boom")

    check = PingHealthCheck("external_api", failing_ping)
    result = await check.check()
    assert result.status is HealthStatus.UNHEALTHY
    assert result.message == "Dependency check failed"


@pytest.mark.asyncio
async def test_health_checker_times_out() -> None:
    async def slow_ping() -> bool:
        return True

    class SlowCheck:
        name = "slow"

        async def check(self):
            import asyncio

            await asyncio.sleep(0.2)
            return await create_ping_health_check("slow", slow_ping).check()

    checker = HealthChecker([SlowCheck()], timeout_seconds=0.01)
    result = await checker.check()
    assert result.checks[0].status is HealthStatus.UNHEALTHY
    assert result.checks[0].message == "Health check timed out"


def test_prometheus_app_exposes_registry() -> None:
    registry = create_registry()
    ObservabilityMetrics.create(registry).errors.labels(boundary="http", code="demo").inc()
    app = create_prometheus_app(registry)
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "errors_total" in response.text


def test_observability_middleware_records_metrics_and_headers(config: ObservabilityConfig) -> None:
    bundle = create_observability_bundle(config)
    logger = structlog.get_logger()

    async def homepage(_request) -> PlainTextResponse:
        return PlainTextResponse("ok")

    app = Starlette(
        routes=[Route("/demo", homepage)],
        middleware=[
            Middleware(
                ObservabilityMiddleware,
                config=config,
                metrics=bundle.metrics,
                tracer=bundle.tracer,
                logger=logger,
            )
        ],
    )
    client = TestClient(app)
    response = client.get(
        "/demo",
        headers={"X-Request-ID": "req-123", "X-Correlation-ID": "corr-456"},
    )
    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-123"
    assert response.headers["x-correlation-id"] == "corr-456"
    body = generate_latest(bundle.registry).decode("ascii")
    assert "http_requests_total" in body


def test_trace_context_injection_and_extraction() -> None:
    carrier: dict[str, str] = {}
    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer("test")
    with tracer.start_as_current_span("parent"):
        inject_context(carrier)
    token = attach_context(carrier)
    try:
        with client_span(tracer, "child", {"component": "redis"}):
            trace_id, span_id = current_trace_ids()
            assert trace_id
            assert span_id
    finally:
        detach_context(token)


def test_traced_operation_records_exception() -> None:
    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer("test")
    with pytest.raises(ValueError, match="failed"):
        with traced_operation(tracer, "demo", kind=SpanKind.CLIENT):
            raise ValueError("failed")


@pytest.mark.asyncio
async def test_otlp_exporter_lifecycle(config: ObservabilityConfig) -> None:
    exporter = OTLPTracingExporter(config)
    await exporter.start()
    await exporter.shutdown()


@pytest.mark.asyncio
async def test_noop_alert_sink_is_safe() -> None:
    sink = NoOpAlertSink()
    await sink.emit("demo", "warning", {"component": "queue"})


@pytest.mark.asyncio
async def test_vendor_alert_sinks_are_extension_points() -> None:
    sink = AzureMonitorAlertSink()
    await sink.emit("queue_lag", "critical", {"queue": "media"})


def test_observability_config_validates_sampling_ratio() -> None:
    with pytest.raises(ValueError, match="trace_sample_ratio"):
        ObservabilityConfig(
            service_name="demo",
            service_version="1",
            environment="test",
            trace_sample_ratio=1.5,
        )
