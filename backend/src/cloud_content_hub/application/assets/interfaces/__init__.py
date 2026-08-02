"""Asset application interfaces."""

from cloud_content_hub.application.assets.interfaces.asset_repository import (
    AssetDetailsRecord,
    AssetLifecycleStatus,
    AssetMediaRecord,
    AssetRecord,
    AssetSearchCriteria,
    AssetSearchPage,
    AssetType,
    AssetUsageRecord,
    IAssetRepository,
    NewAsset,
    ScanStatus,
)
from cloud_content_hub.application.assets.interfaces.event_publisher import IAssetEventPublisher
from cloud_content_hub.application.assets.interfaces.virus_scan_hook import (
    IVirusScanHook,
    VirusScanRequest,
)

__all__ = [
    "AssetDetailsRecord",
    "AssetLifecycleStatus",
    "AssetMediaRecord",
    "AssetRecord",
    "AssetSearchCriteria",
    "AssetSearchPage",
    "AssetType",
    "AssetUsageRecord",
    "IAssetEventPublisher",
    "IAssetRepository",
    "IVirusScanHook",
    "NewAsset",
    "ScanStatus",
    "VirusScanRequest",
]
