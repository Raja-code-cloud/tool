# Prompts

Prompt construction for content generation lives in `services/content_prompt_service.py`. The
module builds normalized prompts for `AIGenerationPort` without embedding provider-specific syntax.

## Inputs mapped to prompts

| Generation input                      | Prompt usage                                         |
| ------------------------------------- | ---------------------------------------------------- |
| Source title/body                     | Context section in user prompt                       |
| `userPrompt`                          | Explicit user instructions                           |
| `selectionText`                       | Scoped selection for `selection` generation scope    |
| `tone`, `audience`, `length`          | System prompt modifiers                              |
| `language`                            | System prompt locale directive                       |
| `callToAction`, `hashtags`            | User prompt sections                                 |
| Asset references (`posterAssetId`, …) | Metadata references (IDs only, no blob content)      |
| `targetPlatforms`                     | System prompt platform list and length constraints   |
| `scope`                               | System prompt scope directive                        |
| `parameters`                          | Passed as AI request temperature/max token overrides |

## Prompt structure

```
System: role + platform constraints + language + scope + tone/audience/length
User:   source content + user instructions + selection + CTA + hashtags + asset refs
```

## Metadata and tracing

`BuiltPrompt` captures:

- `system_prompt_hash` and `user_prompt_hash` (SHA-256, for audit without logging raw text)
- Stable metadata keys: `model`, `scope`, `platforms`, `language`

Preview responses surface these as `PromptMetadataDto`. Workers should persist hashes and template
IDs on generation outputs, not raw prompts, per observability guidelines.

## Validation before prompt build

`ContentValidator` enforces:

- Maximum user prompt size (10,000 characters)
- Valid BCP-47 language tags
- Hashtag count and format per selected platforms
- Parameter count limits
- Required `selectionText` when scope is `selection`

Platform-specific maximum text lengths come from `PlatformMappingService` and are injected into
the system prompt so the model respects the strictest selected platform limit.

## Templates

When `promptTemplateId` is supplied on the request, infrastructure resolves the template and
variables at worker time. The application module records the template ID on
`NewGenerationRequest` and exposes it through generation metadata; it does not render DB templates
directly (that remains infrastructure prompt-layer responsibility per `docs/backend/ai/PROMPT_LAYER.md`).

## AI port boundary

`ContentPromptService.to_application_request()` produces `ApplicationGenerationRequest` consumed by
`AIGenerationPort`. No OpenAI, Anthropic, or Gemini imports appear in the content module.
