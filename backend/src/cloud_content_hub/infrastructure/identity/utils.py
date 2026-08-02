"""Shared identity infrastructure helpers."""

from __future__ import annotations

import base64
import hashlib
import secrets
from datetime import UTC, datetime, timedelta


def utc_now() -> datetime:
    return datetime.now(tz=UTC)


def generate_state() -> str:
    return secrets.token_urlsafe(32)


def generate_nonce() -> str:
    return secrets.token_urlsafe(32)


def generate_code_verifier() -> str:
    return secrets.token_urlsafe(64)[:96]


def generate_code_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def expires_in_minutes(minutes: int) -> datetime:
    return utc_now() + timedelta(minutes=minutes)


def expires_in_days(days: int) -> datetime:
    return utc_now() + timedelta(days=days)


def duration_ms(started_at: datetime, finished_at: datetime | None = None) -> int:
    end = finished_at or utc_now()
    return max(int((end - started_at).total_seconds() * 1000), 0)
