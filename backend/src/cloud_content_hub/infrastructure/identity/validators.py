"""OAuth and token validation helpers."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from .exceptions import OAuthValidationError

REDIRECT_URI_PATTERN = re.compile(r"^https?://")
STATE_PATTERN = re.compile(r"^[A-Za-z0-9._-]{16,128}$")
NONCE_PATTERN = re.compile(r"^[A-Za-z0-9._-]{16,128}$")
PKCE_VERIFIER_PATTERN = re.compile(r"^[A-Za-z0-9._~-]{43,128}$")


def validate_redirect_uri(redirect_uri: str, *, allowed: tuple[str, ...], https_only: bool) -> None:
    if redirect_uri not in allowed:
        raise OAuthValidationError("redirect_uri is not registered")
    parsed = urlparse(redirect_uri)
    if not parsed.scheme or not parsed.netloc:
        raise OAuthValidationError("redirect_uri is malformed")
    if https_only and parsed.scheme != "https":
        raise OAuthValidationError("redirect_uri must use HTTPS")


def validate_state(state: str, expected_state: str) -> None:
    if not STATE_PATTERN.fullmatch(state):
        raise OAuthValidationError("state has invalid format")
    if state != expected_state:
        raise OAuthValidationError("state mismatch")


def validate_nonce(token_nonce: str | None, expected_nonce: str) -> None:
    if not NONCE_PATTERN.fullmatch(expected_nonce):
        raise OAuthValidationError("nonce has invalid format")
    if token_nonce != expected_nonce:
        raise OAuthValidationError("nonce mismatch")


def validate_code_verifier(code_verifier: str) -> None:
    if not PKCE_VERIFIER_PATTERN.fullmatch(code_verifier):
        raise OAuthValidationError("code_verifier has invalid format")


def validate_authorization_code(code: str) -> None:
    if not code or len(code) > 2048:
        raise OAuthValidationError("authorization code is invalid")


def extract_bearer_token(authorization_header: str | None) -> str | None:
    if not authorization_header:
        return None
    scheme, _, token = authorization_header.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return None
    return token.strip()
