"""Validate migration consistency expectations after database recovery."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = BACKEND_ROOT / "migrations" / "versions"


def test_initial_schema_migration_exists() -> None:
    initial = MIGRATIONS_DIR / "bd3726e86063_initial_schema.py"
    assert initial.exists()


def test_migration_guide_documents_head_revision() -> None:
    guide = (
        Path(__file__).resolve().parents[3] / "docs" / "backend" / "database" / "MIGRATION_GUIDE.md"
    )
    content = guide.read_text(encoding="utf-8")

    assert "bd3726e86063" in content
    assert "86" in content


@pytest.mark.integration
def test_migrated_database_matches_alembic_head() -> None:
    database_url = os.getenv("DATABASE_URL") or os.getenv("CCH_DATABASE_URL")
    if database_url is None:
        pytest.skip("DATABASE_URL or CCH_DATABASE_URL is not configured.")

    environment = os.environ.copy()
    environment["CCH_DATABASE_URL"] = database_url

    heads = subprocess.run(
        ["alembic", "heads"],
        cwd=BACKEND_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    )
    current = subprocess.run(
        ["alembic", "current"],
        cwd=BACKEND_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    )

    head_revision = heads.stdout.strip().split()[0]
    assert head_revision in current.stdout
