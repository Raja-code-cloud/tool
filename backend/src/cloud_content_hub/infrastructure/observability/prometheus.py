"""Minimal ASGI Prometheus exporter app."""

from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest
from starlette.types import Receive, Scope, Send


class PrometheusASGIApp:
    """Serve one registry without coupling it to business endpoint wiring."""

    def __init__(self, registry: CollectorRegistry) -> None:
        self._registry = registry

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        del receive
        if scope["type"] != "http":
            return
        body = generate_latest(self._registry)
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    (b"content-type", CONTENT_TYPE_LATEST.encode("ascii")),
                    (b"content-length", str(len(body)).encode("ascii")),
                    (b"cache-control", b"no-store"),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})


def create_prometheus_app(registry: CollectorRegistry) -> PrometheusASGIApp:
    return PrometheusASGIApp(registry)
