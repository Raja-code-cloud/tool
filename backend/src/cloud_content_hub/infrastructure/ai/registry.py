"""Runtime provider registration without adapter coupling."""

from collections.abc import Callable

from cloud_content_hub.infrastructure.ai.config import ProviderConfig, ProviderKind
from cloud_content_hub.infrastructure.ai.exceptions import AIConfigurationError
from cloud_content_hub.infrastructure.ai.interfaces.provider import AIProvider

ProviderBuilder = Callable[..., AIProvider]


class ProviderRegistry:
    def __init__(self) -> None:
        self._builders: dict[ProviderKind, ProviderBuilder] = {}

    def register(self, kind: ProviderKind, builder: ProviderBuilder) -> None:
        if kind in self._builders:
            raise AIConfigurationError(f"Provider already registered: {kind}")
        self._builders[kind] = builder

    def get_builder(self, kind: ProviderKind) -> ProviderBuilder:
        try:
            return self._builders[kind]
        except KeyError as exc:
            raise AIConfigurationError(f"Provider is not registered: {kind}") from exc

    def create(self, config: ProviderConfig) -> AIProvider:
        return self.get_builder(config.kind)(config)

    def registered_kinds(self) -> frozenset[ProviderKind]:
        return frozenset(self._builders)
