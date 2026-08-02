"""Metadata extraction for uploaded asset media."""

from __future__ import annotations

import hashlib
import struct
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import PurePosixPath

from cloud_content_hub.application.assets.interfaces.asset_repository import AssetType


@dataclass(frozen=True, slots=True)
class ExtractedMetadata:
    """Immutable metadata extracted from uploaded bytes."""

    checksum_sha256: str
    extension: str
    values: Mapping[str, str]


class AssetMetadataService:
    """Extracts immutable upload metadata from file bytes."""

    def extract(
        self,
        *,
        asset_type: AssetType,
        filename: str,
        content_type: str,
        file_data: bytes,
        checksum_sha256: str | None,
    ) -> ExtractedMetadata:
        """Extract checksum, extension, and lightweight media facts."""

        digest = checksum_sha256 or hashlib.sha256(file_data).hexdigest()
        extension = PurePosixPath(filename).suffix.lower().lstrip(".")
        values: dict[str, str] = {
            "contentType": content_type,
            "extension": extension,
            "byteSize": str(len(file_data)),
        }
        if asset_type in {AssetType.POSTER, AssetType.THUMBNAIL}:
            dimensions = _extract_image_dimensions(file_data, content_type)
            if dimensions is not None:
                values["width"], values["height"] = dimensions
        return ExtractedMetadata(checksum_sha256=digest, extension=extension, values=values)


def _extract_image_dimensions(data: bytes, content_type: str) -> tuple[str, str] | None:
    if content_type == "image/png" and len(data) >= 24 and data[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = struct.unpack(">II", data[16:24])
        return str(width), str(height)
    if content_type == "image/jpeg" and len(data) >= 4 and data[:2] == b"\xff\xd8":
        return _jpeg_dimensions(data)
    if (
        content_type == "image/webp"
        and len(data) >= 30
        and data[:4] == b"RIFF"
        and data[8:12] == b"WEBP"
    ):
        return _webp_dimensions(data)
    return None


def _jpeg_dimensions(data: bytes) -> tuple[str, str] | None:
    index = 2
    length = len(data)
    while index + 9 < length:
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        if marker in {0xC0, 0xC1, 0xC2}:
            height, width = struct.unpack(">HH", data[index + 5 : index + 9])
            return str(width), str(height)
        segment_length = struct.unpack(">H", data[index + 2 : index + 4])[0]
        index += 2 + segment_length
    return None


def _webp_dimensions(data: bytes) -> tuple[str, str] | None:
    chunk_type = data[12:16]
    if chunk_type == b"VP8 " and len(data) >= 30:
        width, height = struct.unpack("<HH", data[26:30])
        return str(width & 0x3FFF), str(height & 0x3FFF)
    if chunk_type == b"VP8L" and len(data) >= 25:
        bits = int.from_bytes(data[21:25], "little")
        width = (bits & 0x3FFF) + 1
        height = ((bits >> 14) & 0x3FFF) + 1
        return str(width), str(height)
    if chunk_type == b"VP8X" and len(data) >= 30:
        width = 1 + int.from_bytes(data[24:27], "little")
        height = 1 + int.from_bytes(data[27:30], "little")
        return str(width), str(height)
    return None
