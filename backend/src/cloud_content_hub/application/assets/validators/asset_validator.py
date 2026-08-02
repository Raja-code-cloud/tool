"""Asset business validation."""

from __future__ import annotations

import hashlib
from pathlib import PurePosixPath

from cloud_content_hub.application.assets.dto.requests import (
    CopyAssetRequestDto,
    MoveAssetRequestDto,
    ReplaceAssetRequestDto,
    UploadAssetRequestDto,
)
from cloud_content_hub.application.assets.exceptions.asset_errors import (
    AssetChecksumMismatchError,
    AssetExtensionError,
    AssetMediaTypeError,
    AssetStateError,
    AssetUploadValidationError,
)
from cloud_content_hub.application.assets.interfaces.asset_repository import (
    AssetLifecycleStatus,
    AssetRecord,
    AssetType,
)

_IMAGE_LIMIT = 10 * 1024 * 1024
_ARTICLE_LIMIT = 25 * 1024 * 1024
_VIDEO_LIMIT = 2 * 1024 * 1024 * 1024
_DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

_ALLOWED_MEDIA: dict[AssetType, frozenset[tuple[str, int]]] = {
    AssetType.POSTER: frozenset(
        {
            ("image/jpeg", _IMAGE_LIMIT),
            ("image/png", _IMAGE_LIMIT),
            ("image/webp", _IMAGE_LIMIT),
        }
    ),
    AssetType.THUMBNAIL: frozenset(
        {
            ("image/jpeg", _IMAGE_LIMIT),
            ("image/png", _IMAGE_LIMIT),
            ("image/webp", _IMAGE_LIMIT),
        }
    ),
    AssetType.ARTICLE: frozenset(
        {
            ("text/plain", _ARTICLE_LIMIT),
            ("text/markdown", _ARTICLE_LIMIT),
            ("application/pdf", _ARTICLE_LIMIT),
            (_DOCX_MIME, _ARTICLE_LIMIT),
        }
    ),
    AssetType.VIDEO: frozenset(
        {
            ("video/mp4", _VIDEO_LIMIT),
            ("video/webm", _VIDEO_LIMIT),
            ("video/quicktime", _VIDEO_LIMIT),
        }
    ),
}

_ALLOWED_EXTENSIONS: dict[AssetType, frozenset[str]] = {
    AssetType.POSTER: frozenset({"jpg", "jpeg", "png", "webp"}),
    AssetType.THUMBNAIL: frozenset({"jpg", "jpeg", "png", "webp"}),
    AssetType.ARTICLE: frozenset({"txt", "md", "pdf", "docx"}),
    AssetType.VIDEO: frozenset({"mp4", "webm", "mov"}),
}


def validate_upload_request(request: UploadAssetRequestDto) -> AssetType:
    """Validate upload business rules and return the resolved asset type."""

    asset_type = AssetType(request.asset_type.value)
    _validate_filename(request.filename)
    _validate_extension(asset_type, request.filename)
    _validate_media_pair(asset_type, request.content_type, request.content_length)
    _validate_checksum(request.file_data, request.checksum_sha256)
    return asset_type


def validate_replace_request(asset: AssetRecord, request: ReplaceAssetRequestDto) -> None:
    """Validate asset replacement business rules."""

    if asset.lifecycle_status != AssetLifecycleStatus.ACTIVE:
        raise AssetStateError(detail="Only active assets can be replaced.")
    _validate_filename(request.filename)
    _validate_extension(asset.asset_type, request.filename)
    _validate_media_pair(asset.asset_type, request.content_type, request.content_length)
    _validate_checksum(request.file_data, request.checksum_sha256)


def validate_deletion(asset: AssetRecord) -> None:
    """Validate that an asset can be soft-deleted."""

    if asset.lifecycle_status == AssetLifecycleStatus.ARCHIVED:
        raise AssetStateError(detail="Archived assets cannot be deleted through this operation.")


def validate_restore(asset: AssetRecord) -> None:
    """Validate that an asset can be restored."""

    if not asset.is_deleted:
        raise AssetStateError(detail="Only deleted assets can be restored.")


def validate_archive(asset: AssetRecord) -> None:
    """Validate that an asset can be archived."""

    if asset.lifecycle_status == AssetLifecycleStatus.ARCHIVED:
        raise AssetStateError(detail="The asset is already archived.")
    if asset.lifecycle_status == AssetLifecycleStatus.DRAFT:
        raise AssetStateError(detail="Draft assets must be activated before archiving.")


def validate_tagging(asset: AssetRecord) -> None:
    """Validate that an asset can be tagged."""

    if asset.lifecycle_status == AssetLifecycleStatus.ARCHIVED:
        raise AssetStateError(detail="Archived assets cannot be tagged.")


def validate_move(asset: AssetRecord, request: MoveAssetRequestDto) -> None:
    """Validate that an asset can be moved."""

    if asset.lifecycle_status == AssetLifecycleStatus.ARCHIVED:
        raise AssetStateError(detail="Archived assets cannot be moved.")
    if request.project_id is None and request.folder_id is None:
        raise AssetUploadValidationError(detail="Move requires a project or folder destination.")


def validate_copy(asset: AssetRecord, request: CopyAssetRequestDto) -> None:
    """Validate that an asset can be copied."""

    if asset.lifecycle_status == AssetLifecycleStatus.ARCHIVED:
        raise AssetStateError(detail="Archived assets cannot be copied.")


def _validate_filename(filename: str) -> None:
    normalized = PurePosixPath(filename.replace("\\", "/")).name
    if not normalized or normalized != filename:
        raise AssetUploadValidationError(detail="Filename must not contain path segments.")


def _validate_extension(asset_type: AssetType, filename: str) -> None:
    extension = PurePosixPath(filename).suffix.lower().lstrip(".")
    allowed = _ALLOWED_EXTENSIONS.get(asset_type, frozenset())
    if extension not in allowed:
        raise AssetExtensionError(
            detail=f"Extension '.{extension}' is not allowed for asset type '{asset_type.value}'.",
            parameters={"assetType": asset_type.value, "extension": extension},
        )


def _validate_media_pair(asset_type: AssetType, content_type: str, content_length: int) -> None:
    allowed = _ALLOWED_MEDIA.get(asset_type, frozenset())
    if (content_type, max(content_length, 0)) not in allowed and not any(
        mime == content_type and content_length <= max_size for mime, max_size in allowed
    ):
        raise AssetMediaTypeError(
            detail=(
                f"Media type '{content_type}' is not allowed for asset type '{asset_type.value}'."
            ),
            parameters={"assetType": asset_type.value, "contentType": content_type},
        )
    for _, max_size in allowed:
        if content_type in {mime for mime, _ in allowed} and content_length > max_size:
            raise AssetUploadValidationError(
                detail="Uploaded file exceeds the maximum allowed size.",
                parameters={"maxBytes": max_size},
            )


def _validate_checksum(data: bytes, checksum_sha256: str | None) -> None:
    if checksum_sha256 is None:
        return
    digest = hashlib.sha256(data).hexdigest()
    if digest != checksum_sha256.lower():
        raise AssetChecksumMismatchError(
            detail="Supplied checksum does not match uploaded file bytes.",
        )
