"""Content business validation."""

from __future__ import annotations

import re
from uuid import UUID

from cloud_content_hub.application.content.dto.requests import (
    GenerationInputDto,
    GenerationRequestDto,
    GenerationScopeDto,
    RegenerationRequestDto,
)
from cloud_content_hub.application.content.exceptions.content_errors import (
    ContentNotFoundError,
    ContentStateError,
    ContentVersionConflictError,
    ContentVersionNotFoundError,
    GenerationOutputNotFoundError,
    GenerationOutputStateError,
    GenerationValidationError,
)
from cloud_content_hub.application.content.interfaces.content_repository import (
    ContentLifecycleStatus,
    ContentRecord,
    ContentVersionRecord,
    GenerationOutputRecord,
    GenerationOutputStatus,
    GenerationScope,
)
from cloud_content_hub.application.content.interfaces.platforms import (
    PLATFORM_CONSTRAINTS,
    ContentPlatform,
)
from cloud_content_hub.application.content.services.platform_mapping_service import (
    PlatformMappingService,
)
from cloud_content_hub.core.errors import FieldViolation

_MAX_USER_PROMPT_LENGTH = 10_000
_MAX_GENERATION_PARAMETERS_SIZE = 50
_MAX_HASHTAG_LENGTH = 100
_LANGUAGE_PATTERN = re.compile(r"^[a-z]{2}(-[A-Z]{2})?$")


def validate_generation_request(request: GenerationRequestDto) -> GenerationScope:
    """Validate generation business rules."""

    if request.scope == GenerationScopeDto.SELECTION and not request.selection_text:
        raise GenerationValidationError(detail="selectionText is required when scope is selection.")
    _validate_generation_inputs(request)
    if len(request.parameters) > _MAX_GENERATION_PARAMETERS_SIZE:
        raise GenerationValidationError(detail="Too many generation parameters were supplied.")
    return GenerationScope(request.scope.value)


def validate_regeneration_request(
    content: ContentRecord | None,
    source_version: ContentVersionRecord | None,
    request: RegenerationRequestDto,
) -> tuple[UUID, GenerationScope]:
    """Validate regeneration business rules and return resolved asset id and scope."""

    if content is None:
        raise ContentNotFoundError(parameters={"contentId": str(request.content_id)})
    if source_version is None:
        raise ContentVersionNotFoundError(
            parameters={"sourceVersionId": str(request.source_version_id)}
        )
    if source_version.asset_id != content.asset_id:
        raise GenerationValidationError(
            detail="Source version does not belong to the content asset."
        )
    if content.lifecycle_status == ContentLifecycleStatus.ARCHIVED:
        raise ContentStateError(detail="Archived content cannot be regenerated.")
    scope = validate_generation_request(request)
    return content.asset_id, scope


def validate_archive(content: ContentRecord | None) -> ContentRecord:
    """Validate archive business rules."""

    if content is None:
        raise ContentNotFoundError()
    if content.lifecycle_status == ContentLifecycleStatus.ARCHIVED:
        return content
    if content.lifecycle_status not in {
        ContentLifecycleStatus.DRAFT,
        ContentLifecycleStatus.ACTIVE,
    }:
        raise ContentStateError(detail="Only draft or active content can be archived.")
    return content


def validate_deletion(content: ContentRecord | None) -> ContentRecord:
    """Validate soft-delete business rules."""

    if content is None:
        raise ContentNotFoundError()
    if content.lifecycle_status == ContentLifecycleStatus.ARCHIVED:
        raise ContentStateError(detail="Archived content must be restored before deletion.")
    return content


def validate_restore(content: ContentRecord | None) -> ContentRecord:
    """Validate restore business rules."""

    if content is None:
        raise ContentNotFoundError()
    if not content.is_deleted:
        raise ContentStateError(detail="Only deleted content can be restored.")
    return content


def validate_duplicate(content: ContentRecord | None) -> ContentRecord:
    """Validate duplicate business rules."""

    if content is None:
        raise ContentNotFoundError()
    if content.lifecycle_status == ContentLifecycleStatus.ARCHIVED:
        raise ContentStateError(detail="Archived content cannot be duplicated.")
    return content


def validate_version_creation(content: ContentRecord | None) -> ContentRecord:
    """Validate create-version business rules."""

    if content is None:
        raise ContentNotFoundError()
    if content.lifecycle_status == ContentLifecycleStatus.ARCHIVED:
        raise ContentStateError(detail="Versions cannot be created for archived content.")
    return content


def validate_approval(
    content: ContentRecord | None,
    output: GenerationOutputRecord | None,
) -> tuple[ContentRecord, GenerationOutputRecord]:
    """Validate approve-content business rules."""

    if content is None:
        raise ContentNotFoundError()
    if output is None:
        raise GenerationOutputNotFoundError()
    if output.status != GenerationOutputStatus.PENDING:
        raise GenerationOutputStateError(detail="Only pending generation outputs can be approved.")
    if output.materialized_version_id is not None:
        raise GenerationOutputStateError(detail="Generation output is already materialized.")
    return content, output


def validate_rejection(
    content: ContentRecord | None,
    output: GenerationOutputRecord | None,
) -> tuple[ContentRecord, GenerationOutputRecord]:
    """Validate reject-content business rules."""

    if content is None:
        raise ContentNotFoundError()
    if output is None:
        raise GenerationOutputNotFoundError()
    if output.status != GenerationOutputStatus.PENDING:
        raise GenerationOutputStateError(detail="Only pending generation outputs can be rejected.")
    return content, output


def validate_expected_version(content: ContentRecord, expected_version: int) -> None:
    """Validate optimistic concurrency for mutating commands."""

    if content.version != expected_version:
        raise ContentVersionConflictError(
            parameters={"contentId": str(content.id), "expectedVersion": expected_version},
        )


def _validate_generation_inputs(request: GenerationInputDto) -> None:
    """Validate shared generation input constraints."""

    if request.user_prompt is not None and len(request.user_prompt) > _MAX_USER_PROMPT_LENGTH:
        raise GenerationValidationError(
            detail="User prompt exceeds the maximum allowed size.",
            errors=(
                FieldViolation(field="userPrompt", code="too_long", message="Prompt too large."),
            ),
        )

    if not _LANGUAGE_PATTERN.match(request.language):
        raise GenerationValidationError(
            detail="Language must be a valid BCP-47 language tag.",
            errors=(
                FieldViolation(
                    field="language", code="invalid_format", message="Invalid language."
                ),
            ),
        )

    if request.target_platforms:
        PlatformMappingService.validate_platform_selection(request.target_platforms)
        _validate_hashtags(request.hashtags, request.target_platforms)
        _validate_generation_size(request)


def _validate_hashtags(hashtags: tuple[str, ...], platforms: tuple[ContentPlatform, ...]) -> None:
    violations: list[FieldViolation] = []
    for index, tag in enumerate(hashtags):
        normalized = tag.lstrip("#")
        if not normalized or len(normalized) > _MAX_HASHTAG_LENGTH:
            violations.append(
                FieldViolation(
                    field=f"hashtags[{index}]",
                    code="invalid_format",
                    message="Hashtag format is invalid.",
                )
            )
    if platforms:
        max_allowed = max(PLATFORM_CONSTRAINTS[platform].max_hashtags for platform in platforms)
        if len(hashtags) > max_allowed:
            violations.append(
                FieldViolation(
                    field="hashtags",
                    code="too_many",
                    message="Too many hashtags for the selected platforms.",
                )
            )
    if violations:
        raise GenerationValidationError(
            detail="One or more hashtags failed validation.",
            errors=tuple(violations),
        )


def _validate_generation_size(request: GenerationInputDto) -> None:
    """Validate requested length against platform constraints."""

    if not request.target_platforms:
        return
    mapping = PlatformMappingService()
    for platform in request.target_platforms:
        constraints = mapping.get_constraints(platform)
        if request.call_to_action and len(request.call_to_action) > constraints.max_text_length:
            raise GenerationValidationError(
                detail=f"Call-to-action exceeds the maximum length for {platform.value}.",
            )
