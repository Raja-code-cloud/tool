"""Content application DTOs."""

from cloud_content_hub.application.content.dto.requests import (
    ApproveContentRequestDto,
    CreateContentVersionRequestDto,
    DuplicateContentRequestDto,
    GenerateContentRequest,
    GenerationRequestDto,
    RegenerationRequestDto,
    RejectContentRequestDto,
)
from cloud_content_hub.application.content.dto.responses import (
    ContentDto,
    ContentPreviewResponse,
    ContentVersionResponse,
    GenerateContentResponse,
    SearchContentResponse,
    VersionComparisonResponse,
)

__all__ = [
    "ApproveContentRequestDto",
    "ContentDto",
    "ContentPreviewResponse",
    "ContentVersionResponse",
    "CreateContentVersionRequestDto",
    "DuplicateContentRequestDto",
    "GenerateContentRequest",
    "GenerateContentResponse",
    "GenerationRequestDto",
    "RegenerationRequestDto",
    "RejectContentRequestDto",
    "SearchContentResponse",
    "VersionComparisonResponse",
]
