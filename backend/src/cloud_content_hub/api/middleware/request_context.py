import time
from uuid import uuid4

from starlette.requests import Request
from starlette.routing import Route
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from cloud_content_hub.core.context import bind_request_context, clear_request_context
from cloud_content_hub.core.logging import get_logger
from cloud_content_hub.core.security import is_valid_request_id

REQUEST_ID_HEADER = "X-Request-ID"
CORRELATION_ID_HEADER = "X-Correlation-ID"


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request = Request(scope)
        supplied_request_id = request.headers.get(REQUEST_ID_HEADER)
        supplied_correlation_id = request.headers.get(CORRELATION_ID_HEADER)
        request_id = supplied_request_id or str(uuid4())
        if not is_valid_request_id(supplied_request_id):
            request_id = str(uuid4())
        correlation_id = supplied_correlation_id or request_id
        if not is_valid_request_id(supplied_correlation_id):
            correlation_id = request_id
        tokens = bind_request_context(request_id, correlation_id)
        started = time.perf_counter()
        status_code = 500

        async def send_with_headers(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                headers = list(message.get("headers", []))
                headers = [
                    (k, v)
                    for k, v in headers
                    if k.lower() not in {b"x-request-id", b"x-correlation-id"}
                ]
                headers.append((b"x-request-id", request_id.encode()))
                headers.append((b"x-correlation-id", correlation_id.encode()))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_with_headers)
            if request.url.path not in {
                "/health",
                "/health/live",
                "/health/ready",
                "/live",
                "/ready",
            }:
                get_logger().info(
                    "http.request.completed",
                    message="HTTP request completed",
                    method=request.method,
                    route=route.path
                    if isinstance((route := request.scope.get("route")), Route)
                    else request.url.path,
                    status=status_code,
                    outcome=(
                        "success"
                        if status_code < 400
                        else "client_error"
                        if status_code < 500
                        else "server_error"
                    ),
                    duration_ms=round((time.perf_counter() - started) * 1000, 2),
                )
        finally:
            clear_request_context(tokens)
