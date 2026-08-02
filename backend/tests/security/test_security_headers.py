"""Security response header validation tests."""

from __future__ import annotations

from cloud_content_hub.security.headers import SecurityHeadersPolicy, validate_response_headers


def test_validate_response_headers_detects_missing_required() -> None:
    missing_required, missing_recommended = validate_response_headers({})
    assert "X-Content-Type-Options" in missing_required
    assert "Content-Security-Policy" in missing_required
    assert "Strict-Transport-Security" in missing_recommended


def test_validate_response_headers_accepts_complete_set() -> None:
    policy = SecurityHeadersPolicy()
    headers = {name: value for name, value in policy.expected_values.items()}
    missing_required, missing_recommended = validate_response_headers(headers, policy=policy)
    assert missing_required == []
    assert missing_recommended == []


def test_health_endpoint_documents_missing_security_headers(security_client) -> None:
    """Regression guard: documents current gap until headers middleware is added."""

    response = security_client.get("/health")
    assert response.status_code == 200
    missing_required, _ = validate_response_headers(dict(response.headers))
    assert missing_required, "Expected security header gap to be tracked until remediated"
