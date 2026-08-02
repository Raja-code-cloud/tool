"""Validate Prometheus alert rule YAML files for syntax and structure."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _alert_files() -> list[Path]:
    alerts_dir = _repo_root() / "backend" / "alerts" / "prometheus"
    return sorted(alerts_dir.glob("*.yml")) + sorted(alerts_dir.glob("*.yaml"))


def validate_alert_file(path: Path) -> list[str]:
    errors: list[str] = []
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        errors.append(f"{path}: root must be a mapping")
        return errors

    groups = raw.get("groups")
    if not isinstance(groups, list) or not groups:
        errors.append(f"{path}: 'groups' must be a non-empty list")
        return errors

    for group in groups:
        if not isinstance(group, dict):
            errors.append(f"{path}: each group must be a mapping")
            continue
        if "name" not in group:
            errors.append(f"{path}: group missing 'name'")
        rules = group.get("rules")
        if not isinstance(rules, list) or not rules:
            errors.append(f"{path}: group '{group.get('name')}' must have rules")
            continue
        for rule in rules:
            if not isinstance(rule, dict):
                errors.append(f"{path}: each rule must be a mapping")
                continue
            if "alert" not in rule and "record" not in rule:
                errors.append(f"{path}: rule must define 'alert' or 'record'")
            if "expr" not in rule:
                errors.append(f"{path}: rule missing 'expr'")
    return errors


def main() -> int:
    files = _alert_files()
    if not files:
        print("No alert rule files found.", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for path in files:
        all_errors.extend(validate_alert_file(path))

    if all_errors:
        for error in all_errors:
            print(error, file=sys.stderr)
        return 1

    print(f"Validated {len(files)} alert rule file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
