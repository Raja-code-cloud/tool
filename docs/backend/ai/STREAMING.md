# Streaming

All providers expose streaming through the same async iterator interface:

```python
async for chunk in provider.stream(request):
    ...
```

## Chunk model

`StreamChunk` includes partial `content`, `model`, `provider`, optional terminal `usage`,
`finish_reason`, and `estimated_cost`.

## Provider behavior

| Provider | Strategy                                        |
| -------- | ----------------------------------------------- |
| OpenAI   | Responses API delta events                      |
| Claude   | Native `messages.stream` text stream            |
| Gemini   | `generate_content_stream`                       |
| Mock     | Word-split simulation with terminal usage chunk |

## Client features

`AIClient.stream()`:

- applies safety hooks before streaming
- skips unhealthy or circuit-open providers
- fails over to the next provider on `AIError`
- optional `stream_timeout_seconds` wraps chunks via `stream_with_timeout()`

## Cancellation

Async cancellation propagates to the underlying SDK iterator when the consumer stops iterating.
Do not shield provider streams unless performing brief cleanup.

## Timeouts

Configure per-provider `timeout_seconds` for SDK calls. Client-level stream timeouts add an
upper bound on idle time between chunks.

## Logging

Stream lifecycle emits metadata-only `ai.stream.succeeded` / `ai.stream.failed` events without
content or prompts.
