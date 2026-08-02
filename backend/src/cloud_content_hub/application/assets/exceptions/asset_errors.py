"""Asset-specific application exceptions."""

from cloud_content_hub.core.errors import ClientError, ConflictError, ValidationError


class AssetNotFoundError(ClientError):
    default_code = "resource_not_found"
    default_detail = "The requested asset was not found."


class AssetUploadValidationError(ValidationError):
    default_code = "validation_failed"
    default_detail = "The asset upload request failed validation."


class AssetStateError(ConflictError):
    default_code = "state_transition_invalid"
    default_detail = "The asset is not in a state that allows this operation."


class AssetChecksumMismatchError(ValidationError):
    default_code = "checksum_mismatch"
    default_detail = "The supplied checksum does not match the uploaded file."


class AssetMediaTypeError(ValidationError):
    default_code = "unsupported_media_type"
    default_detail = "The uploaded media type is not allowed for this asset type."


class AssetDuplicateError(ConflictError):
    default_code = "duplicate_asset"
    default_detail = "An asset with the same content or filename already exists."


class AssetExtensionError(ValidationError):
    default_code = "unsupported_extension"
    default_detail = "The uploaded file extension is not allowed for this asset type."
