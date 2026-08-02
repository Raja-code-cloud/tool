"""RFC 9457 problem details with the v1 failure envelope."""

from __future__ import annotations

from http import HTTPStatus
from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from cloud_content_hub.core.context import request_id_var
from cloud_content_hub.core.errors import (
    ApplicationError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DependencyTimeoutError,
    DependencyUnavailableError,
    FieldViolation,
    QuotaExceededError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError,
)
from cloud_content_hub.core.logging import get_logger
from cloud_content_hub.infrastructure.identity.exceptions import (
    AuthenticationException,
    AuthorizationException,
    IdentityError,
    InvalidToken,
    MissingToken,
    PermissionDenied,
    RoleDenied,
    TokenExpired,
)

PROBLEM_BASE = "https://api.cloudcontenthub.ai/problems"


def _status_for(error: ApplicationError) -> int:
    mappings: tuple[tuple[type[ApplicationError], int], ...] = (
        (ValidationError, 422),
        (AuthenticationError, 401),
        (AuthorizationError, 403),
        (ResourceNotFoundError, 404),
        (ConflictError, 409),
        (RateLimitError, 429),
        (QuotaExceededError, 429),
        (DependencyUnavailableError, 503),
        (DependencyTimeoutError, 504),
    )
    return next((status for error_type, status in mappings if isinstance(error, error_type)), 500)


def _identity_to_application(error: IdentityError) -> ApplicationError:
    if isinstance(error, (MissingToken, TokenExpired, InvalidToken)):
        return AuthenticationError(detail=str(error) or AuthenticationError.default_detail)
    if isinstance(error, AuthenticationException):
        return AuthenticationError(detail=str(error) or AuthenticationError.default_detail)
    if isinstance(error, (PermissionDenied, RoleDenied, AuthorizationException)):
        return AuthorizationError(detail=str(error) or AuthorizationError.default_detail)
    return AuthenticationError(detail=str(error) or AuthenticationError.default_detail)


def _error_details(errors: tuple[FieldViolation, ...]) -> list[dict[str, str]]:
    return [
        {
            **({"field": item.field} if item.field else {}),
            "code": item.code,
            "message": item.message,
        }
        for item in errors
    ]


def problem_response(
    request: Request,
    *,
    status: int,
    code: str,
    detail: str,
    errors: tuple[FieldViolation, ...] = (),
) -> JSONResponse:
    body: dict[str, Any] = {
        "success": False,
        "error": {
            "code": code,
            "message": detail,
            "details": _error_details(errors),
        },
        "type": f"{PROBLEM_BASE}/{code.replace('_', '-')}",
        "title": HTTPStatus(status).phrase,
        "status": status,
        "detail": detail,
        "instance": request.url.path,
        "requestId": request_id_var.get(),
    }
    return JSONResponse(body, status_code=status, media_type="application/problem+json")


async def application_error_handler(request: Request, error: ApplicationError) -> JSONResponse:
    status = _status_for(error)
    log = get_logger()
    if status < 500:
        log.warning("http.request.failed", message=error.detail, error_code=error.code)
    else:
        log.error(
            "http.request.failed",
            message=error.detail,
            error_code=error.code,
            exc_info=True,
        )
    return problem_response(
        request, status=status, code=error.code, detail=error.detail, errors=error.errors
    )


async def identity_error_handler(request: Request, error: IdentityError) -> JSONResponse:
    return await application_error_handler(request, _identity_to_application(error))


async def validation_error_handler(
    request: Request, error: RequestValidationError | PydanticValidationError
) -> JSONResponse:
    malformed = any(item["type"] == "json_invalid" for item in error.errors())
    violations = tuple(
        FieldViolation(
            field=".".join(str(part) for part in item["loc"] if part != "body"),
            code=str(item["type"]),
            message=str(item["msg"]),
        )
        for item in error.errors()
    )
    return problem_response(
        request,
        status=400 if malformed else 422,
        code="invalid_request" if malformed else "validation_failed",
        detail=(
            "The request body contains malformed JSON."
            if malformed
            else "One or more fields failed validation."
        ),
        errors=violations,
    )


async def unexpected_error_handler(request: Request, error: Exception) -> JSONResponse:
    get_logger().exception(
        "http.request.failed",
        message="Unexpected HTTP request failure",
        error_code="internal_error",
    )
    return problem_response(
        request,
        status=500,
        code="internal_error",
        detail="An unexpected error occurred.",
    )


def install_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, cast(Any, application_error_handler))
    app.add_exception_handler(IdentityError, cast(Any, identity_error_handler))
    app.add_exception_handler(RequestValidationError, cast(Any, validation_error_handler))
    app.add_exception_handler(Exception, unexpected_error_handler)
