"""Virus scan hook port for asset media ingestion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class VirusScanRequest:
    """Input passed to the virus scan hook before media is accepted."""

    workspace_id: UUID
    asset_id: UUID
    filename: str
    content_type: str
    byte_size: int
    checksum_sha256: str


class IVirusScanHook(Protocol):
    """Application hook invoked during upload/replace validation."""

    async def validate_acceptance(self, request: VirusScanRequest) -> None:
        """Validate that media may be accepted for asynchronous scanning.

        Implementations may reject obviously unsafe payloads or record scan intent.
        Final scan results are applied asynchronously by the media worker.
        """
