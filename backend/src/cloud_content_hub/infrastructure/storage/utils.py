"""Deterministic storage naming and metadata sanitation."""

import re
from collections.abc import Mapping
from datetime import UTC, datetime
from uuid import UUID

from cloud_content_hub.infrastructure.storage.exceptions import StorageValidationError
from cloud_content_hub.infrastructure.storage.models import BlobType
from cloud_content_hub.infrastructure.storage.validators.filename import validate_filename

_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
_METADATA_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,127}$")


def build_blob_name(
    tenant_id: str,
    user_id: str,
    blob_type: BlobType,
    object_id: UUID,
    filename: str,
    *,
    created_at: datetime,
) -> str:
    for label, value in (("tenant", tenant_id), ("user", user_id)):
        if not _IDENTIFIER.fullmatch(value):
            raise StorageValidationError(f"Invalid {label} identifier")
    instant = created_at.astimezone(UTC)
    safe_filename = validate_filename(filename)
    return (
        f"{tenant_id}/{user_id}/{instant:%Y/%m/%d}/{blob_type.value}/"
        f"{object_id.hex}/{safe_filename}"
    )


def sanitize_metadata(metadata: Mapping[str, str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in metadata.items():
        if not _METADATA_KEY.fullmatch(key) or len(value) > 2048:
            raise StorageValidationError("Metadata key or value is invalid")
        if any(character in value for character in "\r\n"):
            raise StorageValidationError("Metadata values cannot contain line breaks")
        result[key] = value
    return result
