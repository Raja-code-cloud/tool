"""Validate restore process documentation and simulated recovery steps."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
RESTORE_GUIDE = REPO_ROOT / "docs" / "backend" / "disaster-recovery" / "RESTORE_GUIDE.md"
BACKEND_ROOT = REPO_ROOT / "backend"

RESTORE_PROCEDURES: tuple[str, ...] = (
    "PostgreSQL",
    "Blob storage",
    "Redis",
    "Secrets",
    "Container",
    "Outbox",
)


def test_restore_guide_documents_all_procedures() -> None:
    content = RESTORE_GUIDE.read_text(encoding="utf-8")

    for procedure in RESTORE_PROCEDURES:
        assert procedure.lower() in content.lower(), f"Restore guide missing: {procedure}"


def test_restore_guide_includes_verification_checklist() -> None:
    content = RESTORE_GUIDE.read_text(encoding="utf-8")

    assert "/live" in content
    assert "/ready" in content
    assert "Alembic" in content


def test_restore_guide_documents_pitr_command() -> None:
    content = RESTORE_GUIDE.read_text(encoding="utf-8")

    assert "postgres flexible-server restore" in content
    assert "restore-time" in content


@pytest.mark.integration
def test_alembic_head_available_after_restore_simulation() -> None:
    """Integration: confirm migration head is reachable on configured database."""

    database_url = os.getenv("DATABASE_URL") or os.getenv("CCH_DATABASE_URL")
    if database_url is None:
        pytest.skip("DATABASE_URL or CCH_DATABASE_URL is not configured.")

    environment = os.environ.copy()
    environment["CCH_DATABASE_URL"] = database_url
    result = subprocess.run(
        ["alembic", "current"],
        cwd=BACKEND_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip(), "Alembic current returned empty output"
