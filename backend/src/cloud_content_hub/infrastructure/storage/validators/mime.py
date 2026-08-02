"""MIME type allowlist validation."""

from collections.abc import Collection

from cloud_content_hub.infrastructure.storage.exceptions import InvalidMimeTypeError

DEFAULT_ALLOWED_MIME_PREFIXES = ("application/", "audio/", "image/", "text/", "video/")


def validate_mime_type(
    content_type: str,
    allowed_prefixes: Collection[str] = DEFAULT_ALLOWED_MIME_PREFIXES,
) -> str:
    normalized = content_type.split(";", maxsplit=1)[0].strip().lower()
    if not normalized or any(character in normalized for character in "\r\n"):
        raise InvalidMimeTypeError("Invalid MIME type")
    if not any(normalized.startswith(prefix) for prefix in allowed_prefixes):
        raise InvalidMimeTypeError("MIME type is not allowed")
    return normalized
