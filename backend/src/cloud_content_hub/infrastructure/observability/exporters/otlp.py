"""OTLP trace exporter lifecycle adapter."""

import asyncio

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased

from ..config import ObservabilityConfig


class OTLPTracingExporter:
    def __init__(self, config: ObservabilityConfig) -> None:
        self._config = config
        self._provider: TracerProvider | None = None

    async def start(self) -> None:
        if not self._config.tracing_enabled or self._provider is not None:
            return
        resource = Resource.create(
            {
                "service.name": self._config.service_name,
                "service.version": self._config.service_version,
                "deployment.environment.name": self._config.environment,
            }
        )
        provider = TracerProvider(
            resource=resource,
            sampler=ParentBased(TraceIdRatioBased(self._config.trace_sample_ratio)),
        )
        if self._config.otlp_endpoint:
            exporter = OTLPSpanExporter(
                endpoint=self._config.otlp_endpoint,
                insecure=self._config.otlp_insecure,
            )
            provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        self._provider = provider

    async def shutdown(self) -> None:
        if self._provider is not None:
            provider, self._provider = self._provider, None
            await asyncio.to_thread(provider.shutdown)
