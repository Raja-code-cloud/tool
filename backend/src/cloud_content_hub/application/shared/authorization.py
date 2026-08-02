"""Authorization helpers for application handlers."""

from __future__ import annotations

from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.core.errors import AuthorizationError


def require_permission(actor: ActorContext, permission: str) -> None:
    """Raise when the actor lacks the required workspace permission."""

    if not actor.has_permission(permission):
        raise AuthorizationError(
            detail=f"Permission '{permission}' is required.",
            parameters={"permission": permission},
        )
