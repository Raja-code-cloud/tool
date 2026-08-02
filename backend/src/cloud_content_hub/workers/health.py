"""Worker process health checks."""

from __future__ import annotations

from dataclasses import dataclass

from cloud_content_hub.bootstrap.container import Container
from cloud_content_hub.infrastructure.events.factory import create_outbox_health_check
from cloud_content_hub.infrastructure.observability.health import AggregateHealth, HealthChecker
from cloud_content_hub.workers.config import WorkerRuntimeConfig


@dataclass(frozen=True, slots=True)
class WorkerHealthService:
    """Exposes worker readiness through shared health infrastructure."""

    checker: HealthChecker
    config: WorkerRuntimeConfig

    @classmethod
    def from_container(
        cls,
        container: Container,
        config: WorkerRuntimeConfig,
    ) -> WorkerHealthService:
        """Build a worker health service from the process container."""

        outbox_probe = create_outbox_health_check(
            container.events,
            session_factory=container.session_factory,
        )
        existing_names = {check.name for check in container.health_checker.checks}
        checks = list(container.health_checker.checks)
        if outbox_probe.name not in existing_names:
            checks.append(outbox_probe)
        checker = HealthChecker(checks, timeout_seconds=config.health_timeout_seconds)
        return cls(checker=checker, config=config)

    async def check(self) -> AggregateHealth:
        """Run all worker health checks concurrently."""

        return await self.checker.run()

    async def check_outbox_lag(self) -> AggregateHealth:
        """Run only outbox lag checks."""

        outbox_only = HealthChecker(
            [check for check in self.checker.checks if check.name == "outbox_dispatch"],
            timeout_seconds=self.config.health_timeout_seconds,
        )
        return await outbox_only.run()


def build_worker_health_service(
    container: Container,
    config: WorkerRuntimeConfig,
) -> WorkerHealthService:
    """Construct a worker health service."""

    return WorkerHealthService.from_container(container, config)
