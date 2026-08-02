"""Supported content generation platforms and constraints."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ContentPlatform(StrEnum):
    """Extensible platform identifiers for content generation."""

    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    X = "x"
    MEDIUM = "medium"
    YOUTUBE = "youtube"


@dataclass(frozen=True, slots=True)
class PlatformConstraints:
    """Platform-specific content limits used during validation and prompt building."""

    platform: ContentPlatform
    max_text_length: int
    max_title_length: int
    max_hashtags: int
    supports_rich_text: bool
    supports_video: bool
    supports_images: bool


PLATFORM_CONSTRAINTS: dict[ContentPlatform, PlatformConstraints] = {
    ContentPlatform.LINKEDIN: PlatformConstraints(
        platform=ContentPlatform.LINKEDIN,
        max_text_length=3000,
        max_title_length=220,
        max_hashtags=5,
        supports_rich_text=False,
        supports_video=True,
        supports_images=True,
    ),
    ContentPlatform.FACEBOOK: PlatformConstraints(
        platform=ContentPlatform.FACEBOOK,
        max_text_length=63206,
        max_title_length=255,
        max_hashtags=30,
        supports_rich_text=True,
        supports_video=True,
        supports_images=True,
    ),
    ContentPlatform.INSTAGRAM: PlatformConstraints(
        platform=ContentPlatform.INSTAGRAM,
        max_text_length=2200,
        max_title_length=150,
        max_hashtags=30,
        supports_rich_text=False,
        supports_video=True,
        supports_images=True,
    ),
    ContentPlatform.X: PlatformConstraints(
        platform=ContentPlatform.X,
        max_text_length=280,
        max_title_length=100,
        max_hashtags=10,
        supports_rich_text=False,
        supports_video=True,
        supports_images=True,
    ),
    ContentPlatform.MEDIUM: PlatformConstraints(
        platform=ContentPlatform.MEDIUM,
        max_text_length=100_000,
        max_title_length=100,
        max_hashtags=5,
        supports_rich_text=True,
        supports_video=False,
        supports_images=True,
    ),
    ContentPlatform.YOUTUBE: PlatformConstraints(
        platform=ContentPlatform.YOUTUBE,
        max_text_length=5000,
        max_title_length=100,
        max_hashtags=15,
        supports_rich_text=False,
        supports_video=True,
        supports_images=True,
    ),
}
