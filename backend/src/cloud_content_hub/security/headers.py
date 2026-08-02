"""Security response header policy used by automated security validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

RECOMMENDED_SECURITY_HEADERS: Final[dict[str, str]] = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "accelerometer=(), camera=(), geolocation=(), microphone=()",
}


@dataclass(frozen=True, slots=True)
class SecurityHeadersPolicy:
    """Expected security headers for API responses."""

    required: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {
                "X-Content-Type-Options",
                "Content-Security-Policy",
                "X-Frame-Options",
                "Referrer-Policy",
            }
        )
    )
    recommended: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {
                "Strict-Transport-Security",
                "Permissions-Policy",
            }
        )
    )
    expected_values: dict[str, str] = field(
        default_factory=lambda: dict(RECOMMENDED_SECURITY_HEADERS)
    )


def validate_response_headers(
    headers: dict[str, str],
    *,
    policy: SecurityHeadersPolicy | None = None,
) -> tuple[list[str], list[str]]:
    """Return missing required and recommended security headers (case-insensitive)."""

    resolved = policy or SecurityHeadersPolicy()
    normalized = {key.lower(): value for key, value in headers.items()}
    missing_required = sorted(
        header for header in resolved.required if header.lower() not in normalized
    )
    missing_recommended = sorted(
        header for header in resolved.recommended if header.lower() not in normalized
    )
    return missing_required, missing_recommended
