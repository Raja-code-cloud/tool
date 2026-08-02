"""Autospecced storage mock factory."""

from unittest.mock import AsyncMock, MagicMock

from cloud_content_hub.infrastructure.storage.interfaces.storage_provider import StorageProvider


def create_mock_storage_provider() -> MagicMock:
    mock = MagicMock(spec=StorageProvider)
    for method in (
        "upload",
        "delete",
        "exists",
        "copy",
        "move",
        "list",
        "generate_sas_url",
        "get_metadata",
        "set_metadata",
        "health_check",
        "close",
    ):
        setattr(mock, method, AsyncMock())
    return mock
