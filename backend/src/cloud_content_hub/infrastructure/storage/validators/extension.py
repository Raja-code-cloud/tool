"""File extension whitelist validation."""

from collections.abc import Collection
from pathlib import PurePosixPath

from cloud_content_hub.infrastructure.storage.exceptions import StorageValidationError


def validate_extension(
    filename: str,
    allowed_extensions: Collection[str],
) -> str:
    extension = PurePosixPath(filename).suffix.lower().lstrip(".")
    if not extension:
        raise StorageValidationError("Filename must include an allowed extension")
    normalized = {item.lower().lstrip(".") for item in allowed_extensions}
    if extension not in normalized:
        raise StorageValidationError("File extension is not allowed")
    return extension
