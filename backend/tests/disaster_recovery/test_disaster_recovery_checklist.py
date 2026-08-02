"""Validate disaster recovery documentation and checklist completeness."""

from __future__ import annotations

from tests.disaster_recovery.helpers.checklist import (
    DISASTER_SCENARIOS,
    RECOVERY_CHECKLIST_ITEMS,
    assert_dr_docs_exist,
    document_mentions_scenario,
    dr_document_paths,
)


def test_required_dr_documents_exist() -> None:
    assert_dr_docs_exist()


def test_dr_documents_are_non_empty() -> None:
    for name, path in dr_document_paths().items():
        content = path.read_text(encoding="utf-8")
        assert len(content) > 200, f"{name} appears incomplete"


def test_runbook_covers_all_disaster_scenarios() -> None:
    runbook = dr_document_paths()["DISASTER_RECOVERY_RUNBOOK.md"].read_text(encoding="utf-8")

    for scenario in DISASTER_SCENARIOS:
        assert document_mentions_scenario(runbook, scenario), (
            f"Runbook missing scenario: {scenario}"
        )


def test_runbook_includes_master_recovery_checklist() -> None:
    runbook = dr_document_paths()["DISASTER_RECOVERY_RUNBOOK.md"].read_text(encoding="utf-8")

    for item in RECOVERY_CHECKLIST_ITEMS:
        keyword = item.split("→")[0].strip().lower()
        assert keyword in runbook.lower(), f"Checklist item not documented: {item}"


def test_rto_rpo_document_defines_objectives() -> None:
    rto_rpo = dr_document_paths()["RTO_RPO.md"].read_text(encoding="utf-8")

    assert "RPO" in rto_rpo
    assert "RTO" in rto_rpo
    assert "PostgreSQL" in rto_rpo
    assert "Redis" in rto_rpo
    assert "Blob storage" in rto_rpo


def test_backup_strategy_documents_retention() -> None:
    backup = dr_document_paths()["BACKUP_STRATEGY.md"].read_text(encoding="utf-8")

    assert "PITR" in backup
    assert "retention" in backup.lower()
    assert "Key Vault" in backup


def test_business_continuity_plan_has_emergency_contacts_placeholder() -> None:
    bcp = dr_document_paths()["BUSINESS_CONTINUITY_PLAN.md"].read_text(encoding="utf-8")

    assert "Emergency contacts" in bcp
    assert "example.com" in bcp


def test_failover_plan_documents_dr_region() -> None:
    failover = dr_document_paths()["FAILOVER_PLAN.md"].read_text(encoding="utf-8")

    assert "westus2" in failover
    assert "dr.bicepparam" in failover
