"""SHA-256 helpers for storage integrity checks."""

import hashlib
import hmac
import re

from cloud_content_hub.infrastructure.storage.exceptions import (
    ChecksumMismatchError,
    StorageValidationError,
)

_SHA256 = re.compile(r"^[a-f0-9]{64}$")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_checksum(checksum: str) -> str:
    normalized = checksum.lower()
    if not _SHA256.fullmatch(normalized):
        raise StorageValidationError("Checksum must be a SHA-256 hexadecimal digest")
    return normalized


def verify_checksum(data: bytes, expected: str) -> str:
    expected_normalized = validate_checksum(expected)
    actual = sha256_hex(data)
    if not hmac.compare_digest(actual, expected_normalized):
        raise ChecksumMismatchError("Content checksum does not match")
    return actual
