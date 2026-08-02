"""Authentication middleware and request-scoped identity context."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from contextvars import ContextVar, Token

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from cloud_content_hub.core.context import correlation_id_var

from .claims import to_unified_identity
from .exceptions import MissingToken
from .jwt import JwtService
from .logging import log_token_validation_failure
from .models import TokenType
from .principal import Principal
from .validators import extract_bearer_token

principal_var: ContextVar[Principal | None] = ContextVar("principal", default=None)


def get_current_principal() -> Principal:
    return principal_var.get() or Principal.anonymous()


def bind_principal(principal: Principal) -> Token[Principal | None]:
    return principal_var.set(principal)


def clear_principal(token: Token[Principal | None]) -> None:
    principal_var.reset(token)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: object, *, jwt_service: JwtService) -> None:
        super().__init__(app)
        self._jwt = jwt_service

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID") or correlation_id_var.get()
        token = extract_bearer_token(request.headers.get("Authorization"))
        principal = Principal.anonymous()
        if token is not None:
            try:
                decoded = await self._jwt.decode_and_verify(token, token_type=TokenType.ACCESS)
                unified = to_unified_identity(decoded.claims)
                principal = Principal.from_unified(unified, claims=decoded.claims)
            except Exception as error:
                log_token_validation_failure(
                    reason=error.__class__.__name__,
                    correlation_id=correlation_id,
                )
        principal_token = bind_principal(principal)
        try:
            response = await call_next(request)
        finally:
            clear_principal(principal_token)
        if correlation_id and "X-Correlation-ID" not in response.headers:
            response.headers["X-Correlation-ID"] = correlation_id
        return response


def require_bearer_token(request: Request) -> str:
    token = extract_bearer_token(request.headers.get("Authorization"))
    if token is None:
        raise MissingToken("bearer token is required")
    return token
