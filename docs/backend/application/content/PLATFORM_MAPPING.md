# Platform Mapping

Platform-specific generation behavior is centralized in `services/platform_mapping_service.py` and
`interfaces/platforms.py`.

## Supported platforms

| Code        | Enum                        | Notes                                 |
| ----------- | --------------------------- | ------------------------------------- |
| `linkedin`  | `ContentPlatform.LINKEDIN`  | Professional posts, 3,000 char limit  |
| `facebook`  | `ContentPlatform.FACEBOOK`  | Rich text supported, large body limit |
| `instagram` | `ContentPlatform.INSTAGRAM` | Caption-focused, hashtag-heavy        |
| `x`         | `ContentPlatform.X`         | Short-form, 280 char default limit    |
| `medium`    | `ContentPlatform.MEDIUM`    | Long-form articles                    |
| `youtube`   | `ContentPlatform.YOUTUBE`   | Descriptions and titles for video     |

## Extensibility

Add a new platform by:

1. Extending `ContentPlatform` enum.
2. Adding a `PlatformConstraints` entry to `PLATFORM_CONSTRAINTS`.
3. Ensuring the social platform catalog row exists in infrastructure (out of module scope).

Validation automatically picks up new entries through `PlatformMappingService.validate_platform_selection`.

## Constraints model

Each platform defines:

| Field                                | Purpose                                                   |
| ------------------------------------ | --------------------------------------------------------- |
| `max_text_length`                    | Body/caption limit for validation and prompt instructions |
| `max_title_length`                   | Title/headline limit                                      |
| `max_hashtags`                       | Hashtag count validation                                  |
| `supports_rich_text`                 | Whether `bodyRich` variants are meaningful                |
| `supports_video` / `supports_images` | Asset reference validation hooks                          |

## Generation outputs

AI workers may emit one `AIGenerationOutput` per target platform (`platform_id` FK). Preview
responses return a `PlatformContentDto` tuple keyed by `ContentPlatform`.

When multiple platforms are selected, preview parsing splits on `\n---\n` section markers when the
segment count matches the platform count; otherwise the full response is duplicated per platform
for display.

## Validation interactions

| Input               | Platform rule                                               |
| ------------------- | ----------------------------------------------------------- |
| `targetPlatforms`   | Required for multi-platform generation; duplicates rejected |
| `hashtags`          | Count capped by max across selected platforms               |
| `callToAction`      | Length checked against strictest `max_text_length`          |
| `length` preference | Combined with platform limits in system prompt              |

## Database alignment

Generation outputs optionally reference `social_platforms.id` via `platform_id`. Application code
uses stable string codes (`ContentPlatform`) at the edge; infrastructure adapters map codes to
catalog UUIDs when persisting outputs.
