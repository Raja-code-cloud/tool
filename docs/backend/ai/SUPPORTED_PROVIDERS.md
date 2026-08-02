# Supported Providers

Adapters live in `infrastructure/ai/providers/`. Each implements `AIProvider` and translates
vendor failures to the local exception vocabulary.

## OpenAI (`openai_provider.py`)

- SDK: `openai.AsyncOpenAI`
- API: Responses API (`responses.create`)
- Capabilities: text, streaming, JSON, tools, vision
- Health: `models.list()` with latency measurement

## Azure OpenAI (`azure_openai_provider.py`)

- SDK: `openai.AsyncAzureOpenAI`
- Requires: `endpoint`, `azure_deployment`, `api_version`, `api_key`
- Shares generation/stream logic with OpenAI adapter
- Provider name: `azure_openai`

## Anthropic Claude (`claude_provider.py`)

- SDK: `anthropic.AsyncAnthropic`
- API: Messages API with native streaming via `messages.stream`
- System messages extracted from `Role.SYSTEM`

## Google Gemini (`gemini_provider.py`)

- SDK: `google.genai.Client` (async via `client.aio`)
- API: `generate_content` / `generate_content_stream`

## Mock (`mock_provider.py`)

- Deterministic, zero-network adapter for tests and local development
- Configurable failure via `fail = True`
- No API key required

## Future placeholder (`future_provider.py`)

- Registered in the default registry as an extension-point stub
- Fails fast with `AIConfigurationError` until a real adapter replaces it
- Demonstrates adding providers without modifying existing adapters

## Adding a provider

1. Add a `ProviderKind` value in `config.py` (when ready for configuration).
2. Implement `AIProvider` in `providers/<name>_provider.py`.
3. Register the builder in `factory.default_registry()`.
4. Add contract tests; do not require live credentials in CI.

Pricing is configured externally via `PricingCatalog` (see `COST_ESTIMATION.md`).
