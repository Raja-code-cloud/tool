"""Default virus scan hook implementation."""

from __future__ import annotations

from cloud_content_hub.application.assets.interfaces.virus_scan_hook import (
    VirusScanRequest,
)


class NoOpVirusScanHook:
    """Accepts all uploads and defers scanning to the media worker."""

    async def validate_acceptance(self, request: VirusScanRequest) -> None:
        """No synchronous rejection; asynchronous scan runs after persistence."""

        _ = request
