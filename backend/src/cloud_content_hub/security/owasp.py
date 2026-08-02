"""OWASP API Security Top 10 (2023) mapping for validation reports."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class OwaspValidationStatus(StrEnum):
    PASS = "pass"
    PARTIAL = "partial"
    FAIL = "fail"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True, slots=True)
class OwaspApiRisk:
    """One OWASP API Security Top 10 (2023) risk category."""

    id: str
    name: str
    description: str
    status: OwaspValidationStatus
    evidence: str
    recommendation: str


def owasp_api_top10_2023() -> tuple[OwaspApiRisk, ...]:
    """Baseline OWASP API Top 10 assessment populated during security review."""

    return (
        OwaspApiRisk(
            id="API1:2023",
            name="Broken Object Level Authorization",
            description="Users must not access objects outside their workspace or tenant.",
            status=OwaspValidationStatus.PARTIAL,
            evidence=(
                "Workspace-scoped repositories require workspace_id; API routes require "
                "X-Workspace-ID and permission dependencies. Membership is not re-validated "
                "at the delivery boundary."
            ),
            recommendation=(
                "Enforce active workspace membership before building ActorContext and add "
                "cross-tenant regression tests for guessed UUIDs."
            ),
        ),
        OwaspApiRisk(
            id="API2:2023",
            name="Broken Authentication",
            description="Authentication mechanisms must resist token forgery and confusion.",
            status=OwaspValidationStatus.PARTIAL,
            evidence=(
                "JWT verification enforces asymmetric algorithms, issuer allowlist, audience, "
                "expiry, and clock skew. Invalid bearer tokens downgrade to anonymous at "
                "middleware; protected routes return 401."
            ),
            recommendation=(
                "Wire RevocationStore in production, add JWT confusion regression tests, and "
                "ensure refresh/session metadata is hashed per SECURITY_GUIDELINES."
            ),
        ),
        OwaspApiRisk(
            id="API3:2023",
            name="Broken Object Property Level Authorization",
            description="Clients must not mutate privileged fields through mass assignment.",
            status=OwaspValidationStatus.PARTIAL,
            evidence=(
                "Pydantic request/response models and handler DTOs constrain writable fields. "
                "No automated mass-assignment regression suite exists."
            ),
            recommendation=(
                "Add security tests that attempt to set admin-only or immutable fields on "
                "create/update payloads."
            ),
        ),
        OwaspApiRisk(
            id="API4:2023",
            name="Unrestricted Resource Consumption",
            description="Expensive endpoints must be rate-limited and bounded.",
            status=OwaspValidationStatus.FAIL,
            evidence=(
                "RateLimitError maps to HTTP 429 but no HTTP rate-limiting middleware or "
                "per-principal quotas are implemented for auth, upload, or generation routes."
            ),
            recommendation=(
                "Add Redis-backed rate limits for authentication, uploads, AI generation, and "
                "publishing with workspace-scoped quotas."
            ),
        ),
        OwaspApiRisk(
            id="API5:2023",
            name="Broken Function Level Authorization",
            description="Administrative functions require explicit authorization.",
            status=OwaspValidationStatus.PARTIAL,
            evidence=(
                "Routes use require_permission() and require_role() dependencies. Admin routes "
                "gate on admin role or scoped permissions."
            ),
            recommendation=(
                "Add regression tests for ordinary roles attempting admin and publishing "
                "maintenance endpoints."
            ),
        ),
        OwaspApiRisk(
            id="API6:2023",
            name="Unrestricted Access to Sensitive Business Flows",
            description="High-impact flows need abuse controls beyond authentication.",
            status=OwaspValidationStatus.PARTIAL,
            evidence=(
                "Idempotency-Key validation exists for mutating routes. OAuth PKCE and state "
                "validation are implemented in the identity provider layer."
            ),
            recommendation=(
                "Add rate limits and step-up authentication for OAuth linking, exports, and "
                "bulk publishing."
            ),
        ),
        OwaspApiRisk(
            id="API7:2023",
            name="Server Side Request Forgery",
            description="Outbound HTTP must reject private and metadata targets.",
            status=OwaspValidationStatus.FAIL,
            evidence="No centralized SSRF guard was found for outbound httpx usage.",
            recommendation=(
                "Introduce an allowlisted outbound HTTP client with DNS resolution checks and "
                "redirect limits for provider integrations."
            ),
        ),
        OwaspApiRisk(
            id="API8:2023",
            name="Security Misconfiguration",
            description="Production defaults must be secure and observable.",
            status=OwaspValidationStatus.PARTIAL,
            evidence=(
                "Production validators reject mock identity, wildcard CORS, and HS/none JWT "
                "algorithms. Security response headers are not emitted by the API layer."
            ),
            recommendation=(
                "Add SecurityHeadersMiddleware at the trusted edge or in FastAPI bootstrap and "
                "disable public OpenAPI in production."
            ),
        ),
        OwaspApiRisk(
            id="API9:2023",
            name="Improper Inventory Management",
            description="All exposed endpoints and versions must be tracked.",
            status=OwaspValidationStatus.PARTIAL,
            evidence=(
                "OpenAPI is versioned under /api/v1 with optional docs at /docs. Health and "
                "metrics endpoints are documented."
            ),
            recommendation=(
                "Maintain an endpoint inventory with owner and auth requirements; disable "
                "undocumented debug routes in production."
            ),
        ),
        OwaspApiRisk(
            id="API10:2023",
            name="Unsafe Consumption of APIs",
            description="Third-party responses must be validated before use.",
            status=OwaspValidationStatus.PARTIAL,
            evidence=(
                "OAuth provider tokens are verified via JWKS. AI and storage provider responses "
                "use typed adapters with bounded error mapping."
            ),
            recommendation=(
                "Validate webhook signatures and provider payload schemas before persistence; "
                "add replay deduplication using webhook_receipt."
            ),
        ),
    )
