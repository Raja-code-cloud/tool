# Observability Logging

The existing structlog configuration remains authoritative. Insert
`observability_processors()` before the JSON renderer to add request, correlation, trace, and span
context, normalize exception metadata, and redact known secret fields.

Events use stable lowercase dotted names and concise safe messages. Route templates replace raw
paths. Do not log query strings, authorization/cookie headers, tokens, passwords, signed URLs,
connection strings, prompts, generated content, provider payloads, SQL parameters, or personal
data.

Unexpected exceptions are logged once at the outer request/job boundary. The safe exception helper
records type names, not exception arguments. Performance helpers emit duration only when the
configured threshold is reached. High-volume success signals belong in metrics, not logs.
