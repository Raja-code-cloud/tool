"""Structured identity logging without sensitive payloads."""

from __future__ import annotations

from datetime import datetime

import structlog

from .utils import duration_ms, utc_now

_logger = structlog.get_logger(__name__)


def log_auth_attempt(*, provider: str, correlation_id: str | None = None) -> None:
    _logger.info(
        "identity.auth.attempt",
        message="Authentication attempt started",
        provider=provider,
        correlation_id=correlation_id,
    )


def log_auth_success(
    *,
    provider: str,
    subject: str,
    started_at: datetime,
    correlation_id: str | None = None,
) -> None:
    _logger.info(
        "identity.auth.success",
        message="Authentication succeeded",
        provider=provider,
        subject=subject,
        duration_ms=duration_ms(started_at, utc_now()),
        correlation_id=correlation_id,
    )


def log_auth_failure(
    *,
    provider: str,
    reason: str,
    started_at: datetime | None = None,
    correlation_id: str | None = None,
) -> None:
    _logger.warning(
        "identity.auth.failure",
        message="Authentication failed",
        provider=provider,
        reason=reason,
        duration_ms=duration_ms(started_at) if started_at else None,
        correlation_id=correlation_id,
    )


def log_token_validation_failure(*, reason: str, correlation_id: str | None = None) -> None:
    _logger.warning(
        "identity.token.validation_failed",
        message="Token validation failed",
        reason=reason,
        correlation_id=correlation_id,
    )


def log_authorization_failure(
    *,
    subject: str,
    permission: str,
    correlation_id: str | None = None,
) -> None:
    _logger.info(
        "identity.authorization.denied",
        message="Authorization denied",
        subject=subject,
        permission=permission,
        correlation_id=correlation_id,
    )
