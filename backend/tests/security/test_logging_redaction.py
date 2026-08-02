"""Logging redaction and sensitive data exposure tests."""

from __future__ import annotations

from cloud_content_hub.infrastructure.identity.config import IdentitySettings
from cloud_content_hub.infrastructure.observability.logging import redact_event
from cloud_content_hub.infrastructure.observability.utils import redact_mapping
from cloud_content_hub.infrastructure.storage.config import AzureStorageConfig, AzureCredentialMode


def test_redact_mapping_masks_secret_keys() -> None:
    redacted = redact_mapping(
        {
            "authorization": "Bearer secret-token",
            "password": "hunter2",
            "refresh_token": "rt-123",
            "api_key": "sk-live",
            "safe_field": "visible",
        }
    )
    assert redacted["authorization"] == "[REDACTED]"
    assert redacted["password"] == "[REDACTED]"
    assert redacted["refresh_token"] == "[REDACTED]"
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["safe_field"] == "visible"


def test_redact_event_processor_masks_nested_secrets() -> None:
    event = redact_event(
        None,
        "info",
        {
            "event": "test",
            "access_token": "jwt-value",
            "connection_string": "DefaultEndpointsProtocol=https;AccountName=x",
            "prompt": "secret prompt",
        },
    )
    assert event["access_token"] == "[REDACTED]"
    assert event["connection_string"] == "[REDACTED]"
    assert event["prompt"] == "[REDACTED]"


def test_identity_settings_hide_signing_key_from_repr() -> None:
    settings = IdentitySettings(signing_key_pem="-----BEGIN PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----")
    rendered = repr(settings)
    assert "PRIVATE KEY" not in rendered
    assert "abc" not in rendered


def test_storage_config_hides_connection_string_from_repr() -> None:
    config = AzureStorageConfig(
        account_url="https://example.blob.core.windows.net",
        credential_mode=AzureCredentialMode.CONNECTION_STRING,
        connection_string="DefaultEndpointsProtocol=https;AccountKey=secret",
    )
    rendered = repr(config)
    assert "AccountKey=secret" not in rendered
