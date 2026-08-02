"""OAuth flow hardening security tests."""

from __future__ import annotations

import pytest

from cloud_content_hub.infrastructure.identity.exceptions import OAuthValidationError
from cloud_content_hub.infrastructure.identity.validators import (
    extract_bearer_token,
    validate_authorization_code,
    validate_code_verifier,
    validate_nonce,
    validate_redirect_uri,
    validate_state,
)
from cloud_content_hub.infrastructure.identity.utils import generate_code_challenge, generate_code_verifier


def test_pkce_verifier_meets_length_requirements() -> None:
    verifier = generate_code_verifier()
    validate_code_verifier(verifier)
    challenge = generate_code_challenge(verifier)
    assert len(challenge) >= 43


def test_redirect_uri_must_be_allowlisted() -> None:
    with pytest.raises(OAuthValidationError, match="not registered"):
        validate_redirect_uri(
            "https://evil.example.test/callback",
            allowed=("https://app.example.test/callback",),
            https_only=True,
        )


def test_redirect_uri_requires_https_in_production_mode() -> None:
    with pytest.raises(OAuthValidationError, match="HTTPS"):
        validate_redirect_uri(
            "http://localhost:3000/callback",
            allowed=("http://localhost:3000/callback",),
            https_only=True,
        )


def test_state_must_match_expected_value() -> None:
    state = "a" * 32
    with pytest.raises(OAuthValidationError, match="mismatch"):
        validate_state(state, "b" * 32)


def test_state_rejects_short_values() -> None:
    with pytest.raises(OAuthValidationError, match="invalid format"):
        validate_state("short", "short")


def test_nonce_must_match_id_token_claim() -> None:
    nonce = "n" * 32
    with pytest.raises(OAuthValidationError, match="mismatch"):
        validate_nonce("other", nonce)


def test_authorization_code_length_is_bounded() -> None:
    with pytest.raises(OAuthValidationError):
        validate_authorization_code("x" * 3000)


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        (None, None),
        ("", None),
        ("Basic abc", None),
        ("Bearer", None),
        ("Bearer   ", None),
        ("Bearer valid-token", "valid-token"),
    ],
)
def test_bearer_token_extraction(header: str | None, expected: str | None) -> None:
    assert extract_bearer_token(header) == expected
