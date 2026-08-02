"""Asset application DTOs."""

from cloud_content_hub.application.assets.dto.requests import (
    CopyAssetRequestDto,
    MoveAssetRequestDto,
    ReplaceAssetRequestDto,
    TagAssetRequestDto,
    UploadAssetRequestDto,
)
from cloud_content_hub.application.assets.dto.responses import (
    AssetDetailsDto,
    AssetDto,
    AssetMediaDto,
    AssetTypeDto,
    AssetUsageDto,
)

__all__ = [
    "AssetDetailsDto",
    "AssetDto",
    "AssetMediaDto",
    "AssetTypeDto",
    "AssetUsageDto",
    "CopyAssetRequestDto",
    "MoveAssetRequestDto",
    "ReplaceAssetRequestDto",
    "TagAssetRequestDto",
    "UploadAssetRequestDto",
]
