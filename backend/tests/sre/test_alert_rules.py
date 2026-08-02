"""Validate alert rule YAML structure (mirrors operations/scripts/validate_alerts.py)."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def _validate_alert_file(path: Path) -> list[str]:
    errors: list[str] = []
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return [f"{path}: root must be a mapping"]

    groups = raw.get("groups")
    if not isinstance(groups, list) or not groups:
        return [f"{path}: 'groups' must be a non-empty list"]

    for group in groups:
        rules = group.get("rules", [])
        for rule in rules:
            if "alert" in rule:
                assert "expr" in rule
                assert "labels" in rule
                assert "annotations" in rule
                assert "runbook" in rule["annotations"]
    return errors


def test_alert_rules_have_runbook_annotations() -> None:
    alert_file = REPO_ROOT / "alerts" / "prometheus" / "alert_rules.yml"
    errors = _validate_alert_file(alert_file)
    assert errors == []

def test_alert_recovery_conditions_documented() -> None:
    """Alerts with 'for' duration auto-resolve when expr is false."""
    alert_file = REPO_ROOT / "alerts" / "prometheus" / "alert_rules.yml"
    raw = yaml.safe_load(alert_file.read_text(encoding="utf-8"))
    for group in raw["groups"]:
        for rule in group["rules"]:
            if "alert" in rule:
                assert "for" in rule, f"{rule['alert']} missing 'for' duration"
