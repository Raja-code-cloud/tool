# Tracing

OpenTelemetry is the tracing API and OTLP is the supported vendor-neutral export transport.
`traceparent` and `tracestate` use standard W3C propagation. Inject context into outbound HTTP
headers and message metadata; extract and attach it at consumers, then always detach the token.

Use server spans for inbound HTTP, consumer spans for workers, and client spans for database,
Redis, external HTTP, Azure, and AI calls. Span names and attributes must be stable and bounded.
Never attach prompts, generated content, SQL parameters, signed URLs, tokens, payloads, or user
identifiers.

Parent-based ratio sampling preserves upstream decisions. Errors are recorded by operation helpers
and exceptions continue to propagate. Exporters are started and shut down by process lifecycle
composition; shutdown flushes in a worker thread to avoid blocking the event loop.
