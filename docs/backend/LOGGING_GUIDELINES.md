# Logging Guidelines

## Standard

Emit newline-delimited structured JSON through the approved logging facade. Logs are operational telemetry, not an audit ledger or data store. Security and material business evidence belongs in append-only `audit_logs`; reliable integration facts belong in outbox/inbox/webhook records.

## Required fields

Every record includes:

- `timestamp` in RFC 3339 UTC;
- `level`;
- `event` as a stable lowercase dotted name;
- `message` as concise safe text;
- `service`, `environment`, `version`;
- `request_id` and `correlation_id` when available;
- `trace_id` and `span_id` when tracing is active.

Add `workspace_id`, `organization_id`, `actor_id`, `job_id`, `event_id`, `provider`, `operation`, `duration_ms`, `outcome`, and stable `error_code` only when relevant and permitted. Use identifiers, not full objects.

## Request and correlation IDs

The edge accepts a client request ID only when it matches the approved format and length; otherwise it generates one. One `request_id` identifies one inbound request. A `correlation_id` follows the logical workflow across HTTP, outbox, queues, workers, and provider callbacks. Each retry/job attempt receives its own request/attempt ID while retaining correlation.

Return the request ID in the response header and problem body. Propagate W3C trace context plus approved correlation metadata through messages. Do not trust correlation fields as authorization inputs.

## Event naming and levels

Use stable event names such as `http.request.completed`, `publication.job.failed`, or `oauth.callback.rejected`. Do not encode IDs or outcomes in event names.

- `debug`: local diagnostic detail, normally disabled in production.
- `info`: successful lifecycle/operational milestones and expected client outcomes.
- `warning`: recoverable abnormal conditions, retries, invalid callbacks, approaching limits.
- `error`: failed operations requiring investigation or exhausted retries.
- `critical`: service-wide loss, corruption risk, or security-critical condition.

Do not log routine health probes or every polling loop at `info`. Use metrics for high-volume counts and latency distributions.

## HTTP access logs

Record method, normalized route template, status, duration, response size, authenticated principal class, workspace ID when resolved, user-agent category, and trusted client-network data according to privacy policy. Never log raw query strings by default; they may contain search terms or signed parameters. Log route templates, not high-cardinality full paths.

## Sensitive data policy

Never log:

- passwords, JWTs, refresh/access tokens, API keys, cookies, authorization headers;
- OAuth ciphertext, encryption keys, managed-secret references, signed URLs;
- full prompts, generated content, drafts, uploads, comments, exports;
- raw webhook/provider payloads, database URLs, connection strings;
- personal email/IP/user-agent values unless explicitly approved and minimized;
- card/bank data or unredacted safe-diff content.

Apply allowlist-based field selection and redaction before serialization. Hash/fingerprint only when there is a documented operational use and approved salt/key. Redaction failures fail closed by dropping the field, not by logging raw data.

## Exceptions

Log unexpected exceptions once at the outer request/job boundary with stack trace and safe context. Expected validation, authorization, conflict, and not-found errors do not need stack traces. Preserve error class and stable application code; provider bodies and SQL parameters remain redacted.

## Audit separation

Audit records are append-only and capture actor, action, target, outcome, source, correlation, and a redacted safe diff. They are written transactionally with material state changes where possible. Application logs cannot substitute for required audit records, and audit events must not be duplicated casually into general logs.

## Configuration and operations

Production log level defaults to `INFO` and is configurable without code changes. Output goes to stdout/stderr for platform collection; application processes do not manage production log files. Collection enforces encryption, access control, region/retention policy, and deletion obligations.

Use sampling for repetitive successful events, never for security alerts, terminal job failures, audit evidence, or error summaries. Alerts should derive from rates and service objectives, not isolated noisy log lines.

## Testing

Tests verify required context propagation, stable event names, request/correlation IDs, and redaction. Security tests inject representative secrets into headers, bodies, provider failures, and exceptions and assert they never appear in captured logs.
