"""Platform mapping and constraint resolution for content generation."""

from __future__ import annotations

from dataclasses import dataclass

from cloud_content_hub.application.content.exceptions.content_errors import (
    GenerationValidationError,
)
from cloud_content_hub.application.content.interfaces.platforms import (
    PLATFORM_CONSTRAINTS,
    ContentPlatform,
    PlatformConstraints,
)
from cloud_content_hub.core.errors import FieldViolation

_SUPPORTED_PLATFORMS = frozenset(ContentPlatform)


@dataclass(frozen=True, slots=True)
class PlatformMappingService:
    """Resolves platform-specific generation constraints."""

    @staticmethod
    def validate_platform_selection(platforms: tuple[ContentPlatform, ...]) -> None:
        """Reject unknown or duplicate platform selections."""

        if not platforms:
            raise GenerationValidationError(detail="At least one target platform must be selected.")
        seen: set[ContentPlatform] = set()
        violations: list[FieldViolation] = []
        for index, platform in enumerate(platforms):
            if platform not in _SUPPORTED_PLATFORMS:
                violations.append(
                    FieldViolation(
                        field=f"targetPlatforms[{index}]",
                        code="unsupported",
                        message=f"Platform '{platform.value}' is not supported.",
                    )
                )
            if platform in seen:
                violations.append(
                    FieldViolation(
                        field=f"targetPlatforms[{index}]",
                        code="duplicate",
                        message="Duplicate platform selection is not allowed.",
                    )
                )
            seen.add(platform)
        if violations:
            raise GenerationValidationError(
                detail="One or more target platforms failed validation.",
                errors=tuple(violations),
            )

    def get_constraints(self, platform: ContentPlatform) -> PlatformConstraints:
        """Return constraints for a supported platform."""

        return PLATFORM_CONSTRAINTS[platform]

    def max_generation_length(self, platforms: tuple[ContentPlatform, ...]) -> int:
        """Return the strictest text length limit across selected platforms."""

        if not platforms:
            return 10_000
        return min(self.get_constraints(platform).max_text_length for platform in platforms)

    def platform_codes(self, platforms: tuple[ContentPlatform, ...]) -> tuple[str, ...]:
        """Return stable platform codes for prompt metadata."""

        return tuple(platform.value for platform in platforms)
