"""Production configuration hardening validation tests."""

from __future__ import annotations

import pytest

from cloud_content_hub.core.config import Environment, Settings
from cloud_content_hub.infrastructure.identity.config import IdentitySettings
from cloud_content_hub.security.owasp import OwaspValidationStatus, owasp_api_top10_2023
from cloud_content_hub.security.risk_register import RiskSeverity, RiskStatus, default_risk_register


def test_production_settings_reject_wildcard_cors() -> None:
    with pytest.raises(ValueError, match="cannot contain '\\*'"):
        Settings(
            environment=Environment.PRODUCTION,
            http_allowed_origins=["*"],
            database_url="postgresql+asyncpg://user:pass@db.example.test/app",
        )


def test_risk_register_has_documented_open_high_risks() -> None:
    register = default_risk_register()
    open_high = [
        entry
        for entry in register.open()
        if entry.severity in {RiskSeverity.HIGH, RiskSeverity.CRITICAL}
    ]
    assert len(open_high) >= 2
    assert all(entry.status is RiskStatus.OPEN for entry in open_high)


def test_owasp_catalog_covers_all_ten_categories() -> None:
    risks = owasp_api_top10_2023()
    assert len(risks) == 10
    assert all(risk.status is not OwaspValidationStatus.NOT_APPLICABLE for risk in risks)


def test_production_identity_requires_https_issuer() -> None:
    with pytest.raises(ValueError, match="HTTPS"):
        IdentitySettings(
            environment="production",
            issuer="http://insecure.example.test",
            mock_enabled=False,
            default_provider="entra",
            entra_enabled=True,
            entra_client_id="client",
            entra_tenant_id="tenant",
            entra_redirect_uris=("https://app.example.test/callback",),
        )
