"""FastAPI delivery-layer dependencies."""

from __future__ import annotations

import re
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated, Any, Protocol, cast
from uuid import UUID

from fastapi import Depends, Header, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_content_hub.api.validators import parse_uuid
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.core.config import Settings
from cloud_content_hub.core.errors import AuthenticationError, ValidationError
from cloud_content_hub.infrastructure.database.session import session_scope
from cloud_content_hub.infrastructure.identity.dependencies import (
    CurrentUser,
)
from cloud_content_hub.infrastructure.identity.dependencies import (
    require_permission as identity_require_permission,
)
from cloud_content_hub.infrastructure.identity.principal import Principal

if TYPE_CHECKING:
    from cloud_content_hub.bootstrap.container import Container

_IDEMPOTENCY_PATTERN = re.compile(r"^\S{8,128}$")


def get_container(request: Request) -> Container:
    from cloud_content_hub.bootstrap.container import Container as RuntimeContainer

    return cast(RuntimeContainer, request.app.state.container)


def get_settings(container: Annotated[Container, Depends(get_container)]) -> Settings:
    return container.settings


async def get_database_session(
    container: Annotated[Container, Depends(get_container)],
) -> AsyncIterator[AsyncSession]:
    async for session in session_scope(container.session_factory):
        yield session


def get_redis(container: Annotated[Container, Depends(get_container)]) -> Redis:
    return container.redis


DatabaseSession = Annotated[AsyncSession, Depends(get_database_session)]
RedisDependency = Annotated[Redis, Depends(get_redis)]


def require_workspace_id(
    x_workspace_id: Annotated[str, Header(alias="X-Workspace-ID")],
) -> UUID:
    return parse_uuid(x_workspace_id, field="X-Workspace-ID")


def optional_workspace_id(
    x_workspace_id: Annotated[str | None, Header(alias="X-Workspace-ID")] = None,
) -> UUID | None:
    if x_workspace_id is None:
        return None
    return parse_uuid(x_workspace_id, field="X-Workspace-ID")


WorkspaceId = Annotated[UUID, Depends(require_workspace_id)]
OptionalWorkspaceId = Annotated[UUID | None, Depends(optional_workspace_id)]


def build_actor_context(principal: Principal, workspace_id: UUID) -> ActorContext:
    if not principal.authenticated:
        raise AuthenticationError(detail="Authentication is required.")
    try:
        user_id = UUID(principal.subject)
    except ValueError as exc:
        raise AuthenticationError(detail="Authenticated subject is not a valid user id.") from exc
    return ActorContext(
        user_id=user_id,
        workspace_id=workspace_id,
        permissions=principal.permissions,
    )


def get_actor(
    principal: CurrentUser,
    workspace_id: WorkspaceId,
) -> ActorContext:
    return build_actor_context(principal, workspace_id)


def get_admin_actor(
    principal: CurrentUser,
    workspace_id: OptionalWorkspaceId,
) -> ActorContext:
    if workspace_id is None:
        try:
            user_id = UUID(principal.subject)
        except ValueError as exc:
            raise AuthenticationError(
                detail="Authenticated subject is not a valid user id.",
            ) from exc
        if not principal.authenticated:
            raise AuthenticationError(detail="Authentication is required.")
        return ActorContext(
            user_id=user_id,
            workspace_id=user_id,
            permissions=principal.permissions,
        )
    return build_actor_context(principal, workspace_id)


Actor = Annotated[ActorContext, Depends(get_actor)]
AdminActor = Annotated[ActorContext, Depends(get_admin_actor)]


def require_permission(permission: str) -> Callable[..., Principal]:
    return identity_require_permission(permission)


def parse_if_match(if_match: Annotated[str, Header(alias="If-Match")]) -> int:
    cleaned = if_match.strip().strip('"')
    try:
        version = int(cleaned)
    except ValueError as exc:
        raise ValidationError(detail="If-Match must be a positive integer ETag.") from exc
    if version < 1:
        raise ValidationError(detail="If-Match must be a positive integer ETag.")
    return version


def optional_if_match(
    if_match: Annotated[str | None, Header(alias="If-Match")] = None,
) -> int | None:
    if if_match is None:
        return None
    return parse_if_match(if_match)


IfMatch = Annotated[int, Depends(parse_if_match)]
OptionalIfMatch = Annotated[int | None, Depends(optional_if_match)]


def require_idempotency_key(
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
) -> str:
    if not _IDEMPOTENCY_PATTERN.fullmatch(idempotency_key):
        raise ValidationError(
            detail="Idempotency-Key must be 8-128 printable non-whitespace characters.",
        )
    return idempotency_key


IdempotencyKey = Annotated[str, Depends(require_idempotency_key)]


class HandlerProvider(Protocol):
    """Protocol for resolving application handlers from the app container."""

    def resolve(self, name: str) -> Any: ...


@dataclass(slots=True)
class HandlerRegistry:
    """Registry of application handlers wired into the delivery layer."""

    handlers: dict[str, Any]

    def resolve(self, name: str) -> Any:
        handler = self.handlers.get(name)
        if handler is None:
            msg = f"Handler '{name}' is not registered."
            raise RuntimeError(msg)
        return handler


def get_handler_registry(request: Request) -> HandlerRegistry:
    registry = getattr(request.app.state, "handlers", None)
    if registry is None:
        container = get_container(request)
        registry = wire_handlers(container)
        request.app.state.handlers = registry
    return cast(HandlerRegistry, registry)


def handler_dependency(name: str) -> Callable[[Request], Any]:
    def dependency(request: Request) -> Any:
        return get_handler_registry(request).resolve(name)

    return dependency


Handlers = Annotated[HandlerRegistry, Depends(get_handler_registry)]


def wire_handlers(container: Container) -> HandlerRegistry:
    """Delegate handler wiring to the bootstrap composition root."""

    from cloud_content_hub.bootstrap.handlers import wire_handlers as bootstrap_wire_handlers

    return bootstrap_wire_handlers(container)
