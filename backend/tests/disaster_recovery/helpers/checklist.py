"""Validate disaster recovery documentation completeness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
DR_DOCS_DIR = REPO_ROOT / "docs" / "backend" / "disaster-recovery"

REQUIRED_DR_DOCUMENTS: frozenset[str] = frozenset(
    {
        "README.md",
        "BACKUP_STRATEGY.md",
        "RESTORE_GUIDE.md",
        "FAILOVER_PLAN.md",
        "RTO_RPO.md",
        "DISASTER_RECOVERY_RUNBOOK.md",
        "BUSINESS_CONTINUITY_PLAN.md",
    }
)

RECOVERY_CHECKLIST_ITEMS: tuple[str, ...] = (
    "PostgreSQL accepting connections",
    "Redis responding to PING",
    "Blob storage health check passing",
    "Key Vault secrets current version loaded",
    "GET /live → 200",
    "GET /ready → 200",
    "Alembic at expected head revision",
    "Worker replicas running",
    "Beat replica exactly 1",
    "Outbox lag within warning threshold",
    "Error rate normalized",
)

DISASTER_SCENARIOS: tuple[str, ...] = (
    "Database unavailable",
    "Redis unavailable",
    "Blob storage unavailable",
    "Container failure",
    "Worker failure",
    "Scheduler (beat) failure",
    "Outbox failure",
    "Provider outage",
    "Regional outage",
)


def dr_document_paths() -> dict[str, Path]:
    """Return expected DR document paths keyed by filename."""

    return {name: DR_DOCS_DIR / name for name in REQUIRED_DR_DOCUMENTS}


def assert_dr_docs_exist() -> None:
    """Raise AssertionError when required DR documents are missing."""

    missing = [name for name in REQUIRED_DR_DOCUMENTS if not (DR_DOCS_DIR / name).exists()]
    if missing:
        message = f"Missing disaster recovery documents: {', '.join(sorted(missing))}"
        raise AssertionError(message)


def document_mentions_scenario(document_text: str, scenario: str) -> bool:
    """Return True when a scenario heading or keyword appears in document text."""

    normalized = scenario.lower()
    text_lower = document_text.lower()
    return normalized in text_lower or normalized.replace(" ", "") in text_lower.replace(" ", "")
