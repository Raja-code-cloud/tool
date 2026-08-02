"""Repository factory registration for the composition root."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cloud_content_hub.application.administration.interfaces.administration_repository import (
    IAdministrationRepository,
)
from cloud_content_hub.application.analytics.interfaces.analytics_repository import (
    IAnalyticsRepository,
)
from cloud_content_hub.application.assets.interfaces.asset_repository import IAssetRepository
from cloud_content_hub.application.content.interfaces.content_repository import (
    IContentRepository,
    IGenerationOutputRepository,
    IGenerationRequestRepository,
)
from cloud_content_hub.application.notifications.interfaces.notification_preference_repository import (  # noqa: E501
    INotificationPreferenceRepository,
)
from cloud_content_hub.application.notifications.interfaces.notification_repository import (
    INotificationRepository,
)
from cloud_content_hub.application.publishing.interfaces.publication_repository import (
    IPublicationRepository,
)
from cloud_content_hub.application.scheduler.interfaces.schedule_repository import (
    IScheduleRepository,
)
from cloud_content_hub.application.social_accounts.interfaces.social_account_repository import (
    ISocialAccountRepository,
)
from cloud_content_hub.application.shared.interfaces.job_queue import IBackgroundJobRepository
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.bootstrap.providers import UnwiredDependency
from cloud_content_hub.infrastructure.repositories.sqlalchemy.adapter_session import resolve_session
from cloud_content_hub.infrastructure.repositories.sqlalchemy.administration_repository import (
    SqlAlchemyAdministrationRepository,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.analytics_repository import (
    SqlAlchemyAnalyticsRepository,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.asset_repository import (
    SqlAlchemyAssetRepository,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.content_repository import (
    SqlAlchemyContentRepository,
    SqlAlchemyGenerationOutputRepository,
    SqlAlchemyGenerationRequestRepository,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.notification_repository import (
    SqlAlchemyNotificationPreferenceRepository,
    SqlAlchemyNotificationRepository,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.publication_repository import (
    SqlAlchemyPublicationRepository,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.schedule_repository import (
    SqlAlchemyScheduleRepository,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.social_account_repository import (
    SqlAlchemySocialAccountRepository,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.unit_of_work import (
    SqlAlchemyUnitOfWork,
)


@dataclass(frozen=True, slots=True)
class RepositoryFactories:
    """Factory callables for unit of work and repository resolution."""

    unit_of_work_factory: Callable[[], IUnitOfWork]
    administration_repository_factory: Callable[[IUnitOfWork], IAdministrationRepository]
    analytics_repository_factory: Callable[[IUnitOfWork], IAnalyticsRepository]
    asset_repository_factory: Callable[[IUnitOfWork], IAssetRepository]
    content_repository_factory: Callable[[IUnitOfWork], IContentRepository]
    generation_repository_factory: Callable[[IUnitOfWork], IGenerationRequestRepository]
    generation_output_repository_factory: Callable[[IUnitOfWork], IGenerationOutputRepository]
    notification_repository_factory: Callable[[IUnitOfWork], INotificationRepository]
    preference_repository_factory: Callable[[IUnitOfWork], INotificationPreferenceRepository]
    publication_repository_factory: Callable[[IUnitOfWork], IPublicationRepository]
    schedule_repository_factory: Callable[[IUnitOfWork], IScheduleRepository]
    social_account_repository_factory: Callable[[IUnitOfWork], ISocialAccountRepository]
    job_repository_factory: Callable[[IUnitOfWork], IBackgroundJobRepository]


def create_repository_factories(
    session_factory: async_sessionmaker[AsyncSession],
) -> RepositoryFactories:
    """Construct repository factories bound to the process session factory."""

    def unit_of_work_factory() -> IUnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory)

    def administration_repository_factory(uow: IUnitOfWork) -> IAdministrationRepository:
        return SqlAlchemyAdministrationRepository(resolve_session(uow))

    def analytics_repository_factory(uow: IUnitOfWork) -> IAnalyticsRepository:
        return SqlAlchemyAnalyticsRepository(resolve_session(uow))

    def asset_repository_factory(uow: IUnitOfWork) -> IAssetRepository:
        return SqlAlchemyAssetRepository(resolve_session(uow))

    def content_repository_factory(uow: IUnitOfWork) -> IContentRepository:
        return SqlAlchemyContentRepository(resolve_session(uow))

    def generation_repository_factory(uow: IUnitOfWork) -> IGenerationRequestRepository:
        return SqlAlchemyGenerationRequestRepository(resolve_session(uow))

    def generation_output_repository_factory(uow: IUnitOfWork) -> IGenerationOutputRepository:
        return SqlAlchemyGenerationOutputRepository(resolve_session(uow))

    def notification_repository_factory(uow: IUnitOfWork) -> INotificationRepository:
        return SqlAlchemyNotificationRepository(resolve_session(uow))

    def preference_repository_factory(uow: IUnitOfWork) -> INotificationPreferenceRepository:
        return SqlAlchemyNotificationPreferenceRepository(resolve_session(uow))

    def publication_repository_factory(uow: IUnitOfWork) -> IPublicationRepository:
        return SqlAlchemyPublicationRepository(resolve_session(uow))

    def schedule_repository_factory(uow: IUnitOfWork) -> IScheduleRepository:
        return SqlAlchemyScheduleRepository(resolve_session(uow))

    def social_account_repository_factory(uow: IUnitOfWork) -> ISocialAccountRepository:
        return SqlAlchemySocialAccountRepository(resolve_session(uow))

    unwired = UnwiredDependency()

    def job_repository_factory(_uow: IUnitOfWork) -> IBackgroundJobRepository:
        return unwired  # type: ignore[return-value]

    return RepositoryFactories(
        unit_of_work_factory=unit_of_work_factory,
        administration_repository_factory=administration_repository_factory,
        analytics_repository_factory=analytics_repository_factory,
        asset_repository_factory=asset_repository_factory,
        content_repository_factory=content_repository_factory,
        generation_repository_factory=generation_repository_factory,
        generation_output_repository_factory=generation_output_repository_factory,
        notification_repository_factory=notification_repository_factory,
        preference_repository_factory=preference_repository_factory,
        publication_repository_factory=publication_repository_factory,
        schedule_repository_factory=schedule_repository_factory,
        social_account_repository_factory=social_account_repository_factory,
        job_repository_factory=job_repository_factory,
    )
