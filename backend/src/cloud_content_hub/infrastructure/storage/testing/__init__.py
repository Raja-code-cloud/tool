"""Storage test doubles and synthetic fixtures."""

from cloud_content_hub.infrastructure.storage.testing.fake import InMemoryStorageProvider
from cloud_content_hub.infrastructure.storage.testing.mock import create_mock_storage_provider

__all__ = ["InMemoryStorageProvider", "create_mock_storage_provider"]
