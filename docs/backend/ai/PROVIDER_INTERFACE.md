# Provider Interface

The canonical contract is `AIProvider` in `interfaces/provider.py`. It is an async `Protocol`
so application code stays decoupled from concrete adapters.

## Methods

| Method                     | Purpose                                            |
| -------------------------- | -------------------------------------------------- |
| `name`                     | Stable provider identifier (`openai`, `claude`, …) |
| `generate(request)`        | Complete a normalized generation request           |
| `stream(request)`          | Async iterator of `StreamChunk` values             |
| `health_check()`           | Connectivity/authentication probe with latency     |
| `count_tokens(request)`    | Prompt token estimate or exact count               |
| `estimate_cost(request)`   | Pre-call cost estimate using configured pricing    |
| `validate_prompt(request)` | Provider-neutral validation result                 |
| `supported_models()`       | Models exposed by this adapter instance            |
| `supported_capabilities()` | Feature flags (`text`, `streaming`, `json`, …)     |
| `close()`                  | Release SDK clients and connections                |

## Request model

`GenerationRequest` contains:

- `messages`: ordered `system` / `user` / `assistant` tuples
- optional overrides: `model`, `temperature`, `max_tokens`, `stream`
- `metadata` and optional `prompt_metadata` for tracing (never logged raw)

## Response model

`GenerationResponse` normalizes:

- generated text, finish reason, provider, model
- `TokenUsage` (input, output, total)
- optional `estimated_cost`, `latency_ms`, `request_id`, `metadata`

Streaming uses `StreamChunk` with the same identifiers and optional terminal usage.

## Construction

Never instantiate adapters directly in application code. Use:

```python
from cloud_content_hub.infrastructure.ai.factory import create_provider
provider = create_provider(config)
```

Or inject `AIClient` from the bootstrap composition root.
