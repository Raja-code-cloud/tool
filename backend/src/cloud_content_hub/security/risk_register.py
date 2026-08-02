"""Structured risk register for security review deliverables."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RiskSeverity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskStatus(StrEnum):
    OPEN = "open"
    MITIGATED = "mitigated"
    ACCEPTED = "accepted"


@dataclass(frozen=True, slots=True)
class RiskEntry:
    """One tracked security risk."""

    id: str
    title: str
    severity: RiskSeverity
    status: RiskStatus
    category: str
    description: str
    evidence: str
    remediation: str
    owner: str = "platform-security"


@dataclass(frozen=True, slots=True)
class RiskRegister:
    """Collection of tracked risks."""

    entries: tuple[RiskEntry, ...]

    def by_severity(self, severity: RiskSeverity) -> tuple[RiskEntry, ...]:
        return tuple(entry for entry in self.entries if entry.severity is severity)

    def open(self) -> tuple[RiskEntry, ...]:
        return tuple(entry for entry in self.entries if entry.status is RiskStatus.OPEN)


def default_risk_register() -> RiskRegister:
    """Return the baseline backend risk register from the security review."""

    return RiskRegister(
        entries=(
            RiskEntry(
                id="R-001",
                title="Missing HTTP security headers",
                severity=RiskSeverity.HIGH,
                status=RiskStatus.OPEN,
                category="API hardening",
                description=(
                    "API responses do not emit HSTS, CSP, X-Content-Type-Options, "
                    "X-Frame-Options, Referrer-Policy, or Permissions-Policy."
                ),
                evidence=(
                    "bootstrap/api.py registers CORS and gzip only; "
                    "no security header middleware."
                ),
                remediation=(
                    "Add SecurityHeadersMiddleware or configure equivalent headers at Azure "
                    "Container Apps / Application Gateway."
                ),
            ),
            RiskEntry(
                id="R-002",
                title="No HTTP rate limiting",
                severity=RiskSeverity.HIGH,
                status=RiskStatus.OPEN,
                category="Abuse prevention",
                description=(
                    "Authentication, upload, generation, and publishing endpoints lack "
                    "per-principal or per-workspace rate limits."
                ),
                evidence="RateLimitError exists but no middleware enforces limits.",
                remediation=(
                    "Implement Redis token-bucket limits keyed by principal and route class."
                ),
            ),
            RiskEntry(
                id="R-003",
                title="Workspace membership not enforced at API boundary",
                severity=RiskSeverity.HIGH,
                status=RiskStatus.OPEN,
                category="Authorization",
                description=(
                    "X-Workspace-ID is required but active membership is not verified before "
                    "ActorContext construction."
                ),
                evidence=(
                    "api/dependencies.py build_actor_context trusts header once authenticated."
                ),
                remediation=(
                    "Resolve membership in delivery dependencies and return 403/404 for "
                    "non-members."
                ),
            ),
            RiskEntry(
                id="R-004",
                title="Worker tasks run with wildcard permissions",
                severity=RiskSeverity.MEDIUM,
                status=RiskStatus.ACCEPTED,
                category="Worker security",
                description=(
                    "Background workers receive permissions=frozenset({'*'}) "
                    "via build_worker_actor."
                ),
                evidence="workers/base.py build_worker_actor grants wildcard permissions.",
                remediation=(
                    "Re-establish least-privilege actor context per task type and validate "
                    "Celery message authenticity."
                ),
            ),
            RiskEntry(
                id="R-005",
                title="No RLS policies in database migrations",
                severity=RiskSeverity.MEDIUM,
                status=RiskStatus.OPEN,
                category="Tenant isolation",
                description=(
                    "Row-level security is documented but not enabled in Alembic migrations."
                ),
                evidence=(
                    "Initial schema migration contains no ENABLE ROW LEVEL SECURITY statements."
                ),
                remediation=(
                    "Add RLS policies and set transaction-local tenant context after authorization."
                ),
            ),
            RiskEntry(
                id="R-006",
                title="Default virus scan hook is no-op",
                severity=RiskSeverity.MEDIUM,
                status=RiskStatus.OPEN,
                category="Upload security",
                description=(
                    "Uploaded content is validated for type/size but not scanned by default."
                ),
                evidence="NoOpVirusScanHook is the default implementation.",
                remediation="Integrate Azure Defender or ClamAV before marking uploads usable.",
            ),
            RiskEntry(
                id="R-007",
                title="RevocationStore not wired in IdentityFactory",
                severity=RiskSeverity.MEDIUM,
                status=RiskStatus.OPEN,
                category="Authentication",
                description="Refresh token revocation exists in tests but is not production-wired.",
                evidence="InMemoryRevocationStore used only in unit tests.",
                remediation="Wire Redis-backed RevocationStore into TokenService at bootstrap.",
            ),
            RiskEntry(
                id="R-008",
                title="No SSRF protection for outbound HTTP",
                severity=RiskSeverity.MEDIUM,
                status=RiskStatus.OPEN,
                category="Integrations",
                description="Outbound httpx calls lack centralized host allowlisting.",
                evidence="No ssrf module or outbound client wrapper found.",
                remediation="Add allowlisted outbound client with private-range rejection.",
            ),
            RiskEntry(
                id="R-009",
                title="CSRF protection protocol only",
                severity=RiskSeverity.LOW,
                status=RiskStatus.OPEN,
                category="Session security",
                description=(
                    "CsrfProtector is defined but cookie-based auth routes are not implemented."
                ),
                evidence="permissions.py defines CsrfProtector protocol only.",
                remediation="Implement CSRF validation when cookie refresh transport is added.",
            ),
            RiskEntry(
                id="R-010",
                title="Dependencies not hash-pinned",
                severity=RiskSeverity.LOW,
                status=RiskStatus.OPEN,
                category="Supply chain",
                description="pyproject.toml uses lower-bound versions without a lockfile.",
                evidence="No requirements.lock or poetry.lock in backend.",
                remediation="Generate lockfile, run pip-audit in CI, and publish SBOM.",
            ),
        )
    )
