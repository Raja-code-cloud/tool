# AI configuration

`ProviderConfig` is a frozen Pydantic v2 model. It includes provider/model selection, secret API
key, Azure endpoint/deployment/API version, timeout, retries, generation defaults, streaming,
rate-limit metadata, and safety policy metadata. Secrets use `SecretStr` and are excluded from
representations. Azure requires endpoint, deployment, and API version. Mock and future
placeholder require no key.

## Provider kinds

| Kind           | Purpose                                       |
| -------------- | --------------------------------------------- |
| `openai`       | OpenAI Responses API                          |
| `azure_openai` | Azure-hosted OpenAI                           |
| `claude`       | Anthropic Messages API                        |
| `gemini`       | Google Gen AI                                 |
| `mock`         | Deterministic test/dev adapter                |
| `future`       | Registered placeholder (fails until replaced) |

## Safety settings

`SafetyConfig` supports:

- `enabled`: master toggle for safety hooks at bootstrap
- `policy`: opaque policy identifier for downstream hooks
- `max_prompt_tokens`: estimated input limit
- `max_prompt_characters`: character limit

## Aggregate config

`AIConfig` groups multiple `ProviderConfig` entries plus optional `primary_kind`, `fallback_kind`,
and `fallback_enabled` for bootstrap wiring.

## Construction helpers

- `create_provider(config)` — single adapter
- `create_client_from_config(config, fallback=...)` — primary/fallback `AIClient`

See `CONFIGURATION_GUIDE.md` for environment variable naming (`CCH_` prefix) at the deployment layer.
