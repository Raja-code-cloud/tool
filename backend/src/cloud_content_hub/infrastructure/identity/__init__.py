"""Identity and authentication infrastructure."""

from cloud_content_hub.infrastructure.identity.config import IdentitySettings
from cloud_content_hub.infrastructure.identity.dependencies import (
    AuthenticatedPrincipal,
    CurrentAdmin,
    CurrentUser,
    OptionalUser,
)
from cloud_content_hub.infrastructure.identity.factory import IdentityFactory
from cloud_content_hub.infrastructure.identity.principal import Principal
from cloud_content_hub.infrastructure.identity.registry import ProviderRegistry

__all__ = [
    "AuthenticatedPrincipal",
    "CurrentAdmin",
    "CurrentUser",
    "IdentityFactory",
    "IdentitySettings",
    "OptionalUser",
    "Principal",
    "ProviderRegistry",
]
