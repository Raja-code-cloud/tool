"""Exporter and alert extension ports."""

from collections.abc import Mapping
from typing import Protocol


class TelemetryExporter(Protocol):
    async def start(self) -> None:
        """Start exporter resources."""

    async def shutdown(self) -> None:
        """Flush and stop exporter resources."""


class AlertSink(Protocol):
    async def emit(
        self,
        name: str,
        severity: str,
        attributes: Mapping[str, str],
    ) -> None:
        """Emit a low-volume operational alert."""
