"""Deployment verification for Alembic migrations and schema baseline."""

from __future__ import annotations

from pathlib import Path

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory

from cloud_content_hub.infrastructure.database.base import Base

pytestmark = pytest.mark.deployment

BACKEND_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = BACKEND_ROOT / "migrations" / "versions"


class TestAlembicMigrations:
    def test_alembic_ini_exists(self) -> None:
        assert (BACKEND_ROOT / "alembic.ini").is_file()

    def test_migrations_directory_has_head_revision(self) -> None:
        revisions = list(MIGRATIONS_DIR.glob("*.py"))
        assert len(revisions) >= 1

    def test_alembic_head_is_reachable(self) -> None:
        config = Config(str(BACKEND_ROOT / "alembic.ini"))
        script = ScriptDirectory.from_config(config)
        head = script.get_current_head()
        assert head is not None

    def test_orm_metadata_table_count(self) -> None:
        import cloud_content_hub.infrastructure.database.models as _models  # noqa: F401

        assert len(Base.metadata.tables) == 86
