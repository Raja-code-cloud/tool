"""Application service registration for the composition root."""

from __future__ import annotations

from dataclasses import dataclass

from cloud_content_hub.application.administration.services.audit_service import AuditService
from cloud_content_hub.application.assets.services.duplicate_detection_service import (
    DuplicateDetectionService,
)
from cloud_content_hub.application.content.services.content_generation_service import (
    ContentGenerationService,
)
from cloud_content_hub.application.content.services.content_prompt_service import (
    ContentPromptService,
)
from cloud_content_hub.application.content.services.platform_mapping_service import (
    PlatformMappingService,
)
from cloud_content_hub.application.shared.interfaces.ai_generation import AIGenerationPort
from cloud_content_hub.bootstrap.repositories import RepositoryFactories


@dataclass(frozen=True, slots=True)
class ApplicationServices:
    """Process-scoped application services wired at the composition root."""

    audit_service: AuditService
    content_generation_service: ContentGenerationService
    duplicate_detection_service: DuplicateDetectionService


def create_application_services(
    *,
    repositories: RepositoryFactories,
    ai_generation_port: AIGenerationPort,
) -> ApplicationServices:
    """Construct shared application services from repository factories and ports."""

    platform_mapping = PlatformMappingService()
    return ApplicationServices(
        audit_service=AuditService(
            administration_repository_factory=repositories.administration_repository_factory,
        ),
        content_generation_service=ContentGenerationService(
            ai_port=ai_generation_port,
            prompt_service=ContentPromptService(platform_mapping=platform_mapping),
            platform_mapping=platform_mapping,
        ),
        duplicate_detection_service=DuplicateDetectionService(),
    )
