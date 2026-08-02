"""Metric extension ports."""

from collections.abc import Mapping
from typing import Protocol


class CounterMetric(Protocol):
    def increment(self, amount: float = 1.0, labels: Mapping[str, str] | None = None) -> None:
        """Increase the counter."""


class GaugeMetric(Protocol):
    def set(self, value: float, labels: Mapping[str, str] | None = None) -> None:
        """Set the gauge."""


class HistogramMetric(Protocol):
    def observe(self, value: float, labels: Mapping[str, str] | None = None) -> None:
        """Record an observation."""


class MetricFactory(Protocol):
    def counter(self, name: str, description: str, labels: tuple[str, ...] = ()) -> CounterMetric:
        """Create or return a counter."""

    def gauge(self, name: str, description: str, labels: tuple[str, ...] = ()) -> GaugeMetric:
        """Create or return a gauge."""

    def histogram(
        self, name: str, description: str, labels: tuple[str, ...] = ()
    ) -> HistogramMetric:
        """Create or return a histogram."""
