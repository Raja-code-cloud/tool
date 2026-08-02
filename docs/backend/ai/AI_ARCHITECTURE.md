# AI Architecture

Cloud Content Hub AI uses a provider-neutral infrastructure layer under
`backend/src/cloud_content_hub/infrastructure/ai/`. Application and worker code depend on
`AIProvider` and `AIClient` protocols only; vendor SDKs remain inside adapters.

## Dependency direction

```text
application/workers -> AIClient / AIProvider (protocol)
infrastructure/ai/providers/* -> vendor SDKs (OpenAI, Anthropic, Google GenAI)
```

## Components

| Component                    | Responsibility                                           |
| ---------------------------- | -------------------------------------------------------- |
| `interfaces/provider.py`     | SDK-free provider contract                               |
| `models.py`                  | Normalized requests, responses, usage, health            |
| `config.py`                  | Typed immutable provider configuration                   |
| `registry.py` / `factory.py` | Register and construct adapters without coupling         |
| `client.py`                  | Health-aware routing, retries, fallback, telemetry hooks |
| `prompts/`                   | Template rendering and validation (no business prompts)  |
| `tokenizer.py` / `usage.py`  | Token estimation and in-process accounting               |
| `cost.py`                    | Externalized per-model pricing catalog                   |
| `retry.py`                   | Transient failure backoff                                |
| `safety.py`                  | Extension hooks for moderation and PII                   |
| `telemetry.py`               | Metadata-only structured logging                         |
| `providers/*`                | Vendor-specific adapters                                 |

## Lifecycle

1. Bootstrap loads `ProviderConfig` / `AIConfig` from environment (see `CONFIGURATION.md`).
2. `create_provider` resolves an adapter from `ProviderRegistry`.
3. `AIClient` receives an ordered provider list (primary, optional fallback).
4. Requests pass safety hooks, health checks, retries, and normalized responses.
5. Adapters are closed explicitly via `AIClient.close()` or composition-root shutdown.

## Extension points

- Register a new adapter with `ProviderRegistry.register` without editing existing providers.
- Inject `SafetyHook`, `CircuitBreaker`, `PricingCatalog`, and `UsageLedger`.
- Replace token estimation per adapter when a vendor exposes exact counts.

## Non-goals

This layer does not implement content workflows, persistence, HTTP routes, or business prompts.
