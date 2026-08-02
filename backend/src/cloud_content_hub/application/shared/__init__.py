"""Shared application-layer primitives."""

from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission

__all__ = ["ActorContext", "require_permission"]
