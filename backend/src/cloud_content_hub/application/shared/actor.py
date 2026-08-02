"""Immutable actor context for application use cases."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ActorContext:
    """Authenticated actor scoped to one workspace."""

    user_id: UUID
    workspace_id: UUID
    permissions: frozenset[str]

    def has_permission(self, required: str) -> bool:
        """Return whether the actor holds the required permission."""

        required_parts = required.split(":")
        return any(
            permission == "*"
            or permission == required
            or (
                permission.endswith(":*")
                and required_parts[: len(permission.split(":")) - 1] == permission.split(":")[:-1]
            )
            for permission in self.permissions
        )
