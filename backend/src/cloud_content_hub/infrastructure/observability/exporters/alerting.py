"""Vendor-neutral alert sink extension points."""

from collections.abc import Mapping


class NoOpAlertSink:
    """Safe default alert sink that records nothing."""

    async def emit(
        self,
        name: str,
        severity: str,
        attributes: Mapping[str, str],
    ) -> None:
        del name, severity, attributes


class AzureMonitorAlertSink(NoOpAlertSink):
    """Extension point for Azure Monitor alert routing."""


class ApplicationInsightsAlertSink(NoOpAlertSink):
    """Extension point for Application Insights custom events and alerts."""


class GrafanaAlertSink(NoOpAlertSink):
    """Extension point for Grafana alertmanager webhook delivery."""


class DatadogAlertSink(NoOpAlertSink):
    """Extension point for Datadog event and monitor notifications."""


class NewRelicAlertSink(NoOpAlertSink):
    """Extension point for New Relic incident and event delivery."""
