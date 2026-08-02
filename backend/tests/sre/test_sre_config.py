"""SRE validation tests for health probes, monitoring config, and alert rules."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_health_liveness_returns_200(client: TestClient) -> None:
    response = client.get("/health/live")
    assert response.status_code == 200


def test_health_readiness_returns_200_or_503(client: TestClient) -> None:
    response = client.get("/health/ready")
    assert response.status_code in {200, 503}


def test_health_informational_returns_200(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200


def test_probe_config_documents_implemented_routes() -> None:
    probes = _read_yaml(REPO_ROOT / "operations" / "probes.yaml")
    assert isinstance(probes, dict)
    api_probes = probes["api"]["probes"]
    assert api_probes["liveness"]["path"] == "/health/live"
    assert api_probes["readiness"]["path"] == "/health/ready"


def test_alert_rules_valid() -> None:
    alert_file = REPO_ROOT / "alerts" / "prometheus" / "alert_rules.yml"
    raw = _read_yaml(alert_file)
    assert isinstance(raw, dict)
    groups = raw["groups"]
    assert len(groups) >= 5
    alert_names = [
        rule["alert"]
        for group in groups
        for rule in group["rules"]
        if "alert" in rule
    ]
    assert "CchApiUnavailable" in alert_names
    assert "CchOutboxBacklog" in alert_names


def test_recording_rules_valid() -> None:
    rules_file = REPO_ROOT / "monitoring" / "prometheus" / "recording_rules.yml"
    raw = _read_yaml(rules_file)
    assert isinstance(raw, dict)
    record_names = [
        rule["record"]
        for group in raw["groups"]
        for rule in group["rules"]
        if "record" in rule
    ]
    assert "cch:api_availability:ratio5m" in record_names
    assert "cch:worker_success:ratio5m" in record_names


def test_grafana_dashboards_exist_and_valid_json() -> None:
    dashboard_dir = REPO_ROOT / "monitoring" / "grafana" / "dashboards"
    expected = {
        "api.json",
        "workers.json",
        "scheduler.json",
        "publishing.json",
        "storage.json",
        "authentication.json",
        "analytics.json",
        "infrastructure.json",
    }
    found = {path.name for path in dashboard_dir.glob("*.json")}
    assert expected == found
    for name in expected:
        data = json.loads((dashboard_dir / name).read_text(encoding="utf-8"))
        assert "title" in data
        assert "panels" in data


def test_capacity_config_has_pool_and_scaling() -> None:
    capacity = _read_yaml(REPO_ROOT / "operations" / "capacity.yaml")
    assert isinstance(capacity, dict)
    assert capacity["database"]["pool_size_per_process"] == 5
    assert "media" in capacity["queues"]["names"]
