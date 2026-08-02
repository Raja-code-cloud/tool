"""In-memory revocation store for tests."""

from __future__ import annotations

from cloud_content_hub.infrastructure.identity.permissions import RevocationStore


class InMemoryRevocationStore(RevocationStore):
    def __init__(self) -> None:
        self._revoked: set[str] = set()

    async def is_revoked(self, token_id: str) -> bool:
        return token_id in self._revoked

    async def revoke(self, token_id: str, expires_at: int) -> None:
        _ = expires_at
        self._revoked.add(token_id)
