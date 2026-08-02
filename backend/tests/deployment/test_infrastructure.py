"""Deployment verification for Docker, scripts, and release documentation."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.deployment

REPO_ROOT = Path(__file__).resolve().parents[3]


class TestDockerArtifacts:
    def test_api_dockerfile_exists(self) -> None:
        assert (REPO_ROOT / "docker" / "Dockerfile").is_file()

    def test_worker_dockerfile_exists(self) -> None:
        assert (REPO_ROOT / "docker" / "Dockerfile.worker").is_file()

    def test_compose_declares_core_services(self) -> None:
        compose = (REPO_ROOT / "docker" / "docker-compose.yml").read_text(encoding="utf-8")
        assert "cloud-content-hub-api" in compose
        assert "postgres:" in compose
        assert "redis:" in compose

    def test_compose_migrate_profile(self) -> None:
        compose = (REPO_ROOT / "docker" / "docker-compose.yml").read_text(encoding="utf-8")
        assert "alembic" in compose
        assert "upgrade" in compose
        assert "head" in compose


class TestDeploymentScripts:
    def test_required_scripts_exist(self) -> None:
        scripts = REPO_ROOT / "deployment" / "scripts"
        for name in ("build-images.sh", "deploy.sh", "migrate.sh", "rollback.sh", "verify-health.sh"):
            assert (scripts / name).is_file(), f"Missing deployment script: {name}"


class TestReleaseDocumentation:
    def test_release_docs_exist(self) -> None:
        release_dir = REPO_ROOT / "docs" / "backend" / "release"
        required = (
            "RC_CHECKLIST.md",
            "GO_LIVE_CHECKLIST.md",
            "ROLLBACK_GUIDE.md",
            "DEPLOYMENT_VALIDATION.md",
            "UPGRADE_GUIDE.md",
            "KNOWN_ISSUES.md",
        )
        for name in required:
            assert (release_dir / name).is_file(), f"Missing release doc: {name}"

    def test_known_issues_documents_health_001(self) -> None:
        content = (REPO_ROOT / "docs" / "backend" / "release" / "KNOWN_ISSUES.md").read_text(
            encoding="utf-8"
        )
        assert "HEALTH-001" in content


class TestBicepSecrets:
    def test_bicep_references_key_vault_secrets(self) -> None:
        content = (REPO_ROOT / "infra" / "container-apps" / "bicep" / "main.bicep").read_text(
            encoding="utf-8"
        )
        assert "CCH-DATABASE-URL" in content
        assert "CCH-REDIS-URL" in content
        assert re.search(r"CCH_ENVIRONMENT", content)
