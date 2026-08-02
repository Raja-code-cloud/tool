"""Aggregate identity health checks."""

from __future__ import annotations

from dataclasses import dataclass

from .interfaces.identity_provider import IdentityProvider
from .models import ProviderHealth
from .registry import ProviderRegistry


@dataclass(frozen=True, slots=True)
class IdentityHealthReport:
    healthy: bool
    providers: tuple[ProviderHealth, ...]


class IdentityHealthService:
    def __init__(self, registry: ProviderRegistry) -> None:
        self._registry = registry

    async def check_all(self) -> IdentityHealthReport:
        results: list[ProviderHealth] = []
        for provider in self._registry.list_enabled():
            results.append(await provider.health_check())
        return IdentityHealthReport(
            healthy=all(item.healthy for item in results) if results else False,
            providers=tuple(results),
        )

    async def check_provider(self, provider: IdentityProvider) -> ProviderHealth:
        return await provider.health_check()
