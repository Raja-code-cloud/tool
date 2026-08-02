"""Validate backup configuration expectations."""

from __future__ import annotations

from pathlib import Path

from tests.backup.helpers.policies import (
    BACKUP_COMPONENTS,
    BLOB_CONTAINERS,
    KEY_VAULT_SECRETS,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKUP_STRATEGY = REPO_ROOT / "docs" / "backend" / "disaster-recovery" / "BACKUP_STRATEGY.md"
ENVIRONMENTS_DOC = REPO_ROOT / "docs" / "backend" / "devops" / "ENVIRONMENTS.md"
DR_BICEPPARAM = REPO_ROOT / "infra" / "container-apps" / "bicep" / "parameters" / "dr.bicepparam"


def test_backup_strategy_documents_all_components() -> None:
    content = BACKUP_STRATEGY.read_text(encoding="utf-8")

    for component in BACKUP_COMPONENTS:
        assert component in content, f"Backup strategy missing component: {component}"


def test_backup_strategy_documents_key_vault_secrets() -> None:
    content = BACKUP_STRATEGY.read_text(encoding="utf-8")

    for secret in KEY_VAULT_SECRETS:
        assert secret in content, f"Backup strategy missing secret: {secret}"


def test_environments_doc_lists_secret_roles() -> None:
    content = ENVIRONMENTS_DOC.read_text(encoding="utf-8")

    for secret in KEY_VAULT_SECRETS:
        assert secret in content


def test_dr_bicepparam_exists_and_targets_westus2() -> None:
    assert DR_BICEPPARAM.exists()
    content = DR_BICEPPARAM.read_text(encoding="utf-8")

    assert "westus2" in content
    assert "dr" in content


def test_blob_containers_documented_in_storage_strategy() -> None:
    container_strategy = REPO_ROOT / "docs" / "backend" / "storage" / "CONTAINER_STRATEGY.md"
    content = container_strategy.read_text(encoding="utf-8")

    for container in BLOB_CONTAINERS:
        assert container in content


def test_automated_backup_verification_command_documented() -> None:
    content = BACKUP_STRATEGY.read_text(encoding="utf-8")

    assert "pytest tests/backup" in content
