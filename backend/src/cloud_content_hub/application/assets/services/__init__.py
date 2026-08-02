"""Asset application services."""

from cloud_content_hub.application.assets.services.asset_metadata_service import (
    AssetMetadataService,
    ExtractedMetadata,
)
from cloud_content_hub.application.assets.services.asset_storage_service import (
    AssetStorageService,
    StorageTarget,
)
from cloud_content_hub.application.assets.services.duplicate_detection_service import (
    DuplicateDetectionService,
)
from cloud_content_hub.application.assets.services.virus_scan_hook import NoOpVirusScanHook

__all__ = [
    "AssetMetadataService",
    "AssetStorageService",
    "DuplicateDetectionService",
    "ExtractedMetadata",
    "NoOpVirusScanHook",
    "StorageTarget",
]
