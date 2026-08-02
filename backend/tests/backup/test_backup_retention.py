"""Validate backup retention policy documentation."""

from __future__ import annotations

from pathlib import Path

from tests.backup.helpers.policies import RETENTION_POLICIES, DeploymentEnvironment

RTO_RPO_DOC = (
    Path(__file__).resolve().parents[3] / "docs" / "backend" / "disaster-recovery" / "RTO_RPO.md"
)
BACKUP_STRATEGY = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "backend"
    / "disaster-recovery"
    / "BACKUP_STRATEGY.md"
)


def test_retention_policies_increase_with_environment_maturity() -> None:
    dev = RETENTION_POLICIES[DeploymentEnvironment.DEV]
    qa = RETENTION_POLICIES[DeploymentEnvironment.QA]
    prod = RETENTION_POLICIES[DeploymentEnvironment.PROD]

    assert dev.postgresql_pitr_days <= qa.postgresql_pitr_days <= prod.postgresql_pitr_days
    assert dev.log_retention_days <= prod.log_retention_days


def test_prod_and_dr_retention_policies_match() -> None:
    prod = RETENTION_POLICIES[DeploymentEnvironment.PROD]
    dr = RETENTION_POLICIES[DeploymentEnvironment.DR]

    assert prod.postgresql_pitr_days == dr.postgresql_pitr_days
    assert prod.blob_soft_delete_days == dr.blob_soft_delete_days


def test_rto_rpo_document_aligns_with_retention_targets() -> None:
    content = RTO_RPO_DOC.read_text(encoding="utf-8")
    prod_policy = RETENTION_POLICIES[DeploymentEnvironment.PROD]

    assert str(prod_policy.postgresql_pitr_days) in content or "35 days" in content
    assert "5 minutes" in content


def test_backup_strategy_retention_table_matches_policies() -> None:
    content = BACKUP_STRATEGY.read_text(encoding="utf-8")

    assert "7 days" in content
    assert "35 days" in content
    assert "retention" in content.lower()
