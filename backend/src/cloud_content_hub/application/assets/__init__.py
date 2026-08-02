"""Asset application module."""

from cloud_content_hub.application.assets.dto.responses import (
    AssetDetailsDto,
    AssetDto,
    AssetMediaDto,
    AssetUsageDto,
)
from cloud_content_hub.application.assets.events import (
    AssetDeleted,
    AssetReplaced,
    AssetRestored,
    AssetUploaded,
)
from cloud_content_hub.application.assets.handlers.archive_asset_handler import ArchiveAssetHandler
from cloud_content_hub.application.assets.handlers.asset_usage_handler import AssetUsageHandler
from cloud_content_hub.application.assets.handlers.copy_asset_handler import CopyAssetHandler
from cloud_content_hub.application.assets.handlers.delete_asset_handler import DeleteAssetHandler
from cloud_content_hub.application.assets.handlers.get_asset_details_handler import (
    GetAssetDetailsHandler,
)
from cloud_content_hub.application.assets.handlers.get_asset_handler import GetAssetHandler
from cloud_content_hub.application.assets.handlers.move_asset_handler import MoveAssetHandler
from cloud_content_hub.application.assets.handlers.replace_asset_handler import ReplaceAssetHandler
from cloud_content_hub.application.assets.handlers.restore_asset_handler import RestoreAssetHandler
from cloud_content_hub.application.assets.handlers.search_assets_handler import (
    ListAssetsHandler,
    SearchAssetsHandler,
)
from cloud_content_hub.application.assets.handlers.tag_asset_handler import TagAssetHandler
from cloud_content_hub.application.assets.handlers.upload_asset_handler import UploadAssetHandler

__all__ = [
    "ArchiveAssetHandler",
    "AssetDeleted",
    "AssetDetailsDto",
    "AssetDto",
    "AssetMediaDto",
    "AssetReplaced",
    "AssetRestored",
    "AssetUploaded",
    "AssetUsageDto",
    "AssetUsageHandler",
    "CopyAssetHandler",
    "DeleteAssetHandler",
    "GetAssetDetailsHandler",
    "GetAssetHandler",
    "ListAssetsHandler",
    "MoveAssetHandler",
    "ReplaceAssetHandler",
    "RestoreAssetHandler",
    "SearchAssetsHandler",
    "TagAssetHandler",
    "UploadAssetHandler",
]
