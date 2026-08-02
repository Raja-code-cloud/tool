"""Content application interfaces."""

from cloud_content_hub.application.content.interfaces.content_repository import (
    ContentLifecycleStatus,
    ContentOrigin,
    ContentRecord,
    ContentSearchCriteria,
    ContentSearchPage,
    ContentVersionDetailRecord,
    ContentVersionRecord,
    GenerationOutputRecord,
    GenerationOutputStatus,
    GenerationScope,
    IContentRepository,
    IGenerationOutputRepository,
    IGenerationRequestRepository,
    NewContentVersion,
    NewGenerationRequest,
    VersionComparisonRecord,
)
from cloud_content_hub.application.content.interfaces.event_publisher import IContentEventPublisher
from cloud_content_hub.application.content.interfaces.platforms import (
    PLATFORM_CONSTRAINTS,
    ContentPlatform,
    PlatformConstraints,
)

__all__ = [
    "PLATFORM_CONSTRAINTS",
    "ContentLifecycleStatus",
    "ContentOrigin",
    "ContentPlatform",
    "ContentRecord",
    "ContentSearchCriteria",
    "ContentSearchPage",
    "ContentVersionDetailRecord",
    "ContentVersionRecord",
    "GenerationOutputRecord",
    "GenerationOutputStatus",
    "GenerationScope",
    "IContentEventPublisher",
    "IContentRepository",
    "IGenerationOutputRepository",
    "IGenerationRequestRepository",
    "NewContentVersion",
    "NewGenerationRequest",
    "PlatformConstraints",
    "VersionComparisonRecord",
]
