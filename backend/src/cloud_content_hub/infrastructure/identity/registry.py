"""Provider registry and lookup."""

from __future__ import annotations

from collections.abc import Mapping

from .exceptions import ConfigurationError
from .interfaces.identity_provider import IdentityProvider
from .models import ProviderDescriptor


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, IdentityProvider] = {}

    def register(self, provider: IdentityProvider) -> None:
        self._providers[provider.name] = provider

    def get(self, name: str) -> IdentityProvider:
        provider = self._providers.get(name)
        if provider is None:
            raise ConfigurationError(f"identity provider is not registered: {name}")
        return provider

    def list_enabled(self) -> tuple[IdentityProvider, ...]:
        return tuple(self._providers.values())

    def descriptors(self) -> tuple[ProviderDescriptor, ...]:
        descriptors: list[ProviderDescriptor] = []
        for provider in self._providers.values():
            descriptors.append(
                ProviderDescriptor(
                    code=provider.name,
                    name=provider.display_name,
                    authorization_url=provider.authorization_base_url,
                    pkce_required=provider.pkce_required,
                    enabled=True,
                )
            )
        return tuple(descriptors)

    def as_mapping(self) -> Mapping[str, IdentityProvider]:
        return dict(self._providers)
