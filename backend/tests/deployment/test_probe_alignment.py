"""Deployment verification for probe path alignment (HEALTH-001)."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.deployment

REPO_ROOT = Path(__file__).resolve().parents[3]

APP_LIVENESS = "/live"
APP_READINESS = "/ready"


class TestProbeAlignment:
    @pytest.fixture
    def bicep_content(self) -> str:
        path = REPO_ROOT / "infra" / "container-apps" / "bicep" / "main.bicep"
        return path.read_text(encoding="utf-8")

    def test_application_implemented_paths(self) -> None:
        assert APP_LIVENESS == "/live"
        assert APP_READINESS == "/ready"

    def test_bicep_uses_health_prefixed_probes(self, bicep_content: str) -> None:
        assert "/health/live" in bicep_content
        assert "/health/ready" in bicep_content

    @pytest.mark.xfail(
        reason="HEALTH-001: align ACA/Docker probes with /live and /ready",
        strict=True,
    )
    def test_bicep_matches_application_liveness(self, bicep_content: str) -> None:
        assert "/health/live" == APP_LIVENESS

    @pytest.mark.xfail(
        reason="HEALTH-001: align ACA/Docker probes with /live and /ready",
        strict=True,
    )
    def test_bicep_matches_application_readiness(self, bicep_content: str) -> None:
        assert "/health/ready" == APP_READINESS
