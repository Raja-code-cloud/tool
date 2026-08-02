# Backend Coding Standards

## Python baseline and tooling

Use the repository-declared supported Python version and pin the production toolchain in `pyproject.toml`. Formatting and linting use Ruff; static typing uses mypy or pyright in strict mode; tests use pytest. CI is authoritative and must run format checks, lint, typing, tests, architecture checks, and dependency/security scanning.

## Style

Follow PEP 8 and automated formatting. Use four spaces, UTF-8, trailing commas in multiline literals, and a maximum configured line length of 100. Prefer small, explicit functions and early returns. Avoid clever metaprogramming, mutable global state, hidden I/O, and boolean parameters whose meaning is unclear.

Imports are at the top of the module in standard-library, third-party, and local groups. Inline imports require a documented unavoidable circular-dependency reason. Wildcard imports are prohibited.

## Naming

- Modules, functions, variables: `snake_case`
- Classes, protocols, exceptions: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private implementation details: leading underscore
- Commands use imperative names (`SchedulePublication`); events use past tense (`PublicationScheduled`)
- Predicates start with `is_`, `has_`, or `can_`
- Include units in names (`timeout_seconds`, `duration_ms`)

Use business vocabulary from the database documentation. Never collapse organization and workspace into “tenant,” or the four independent lifecycle state machines into one status.

## Typing

All public and nontrivial internal functions are fully typed. Avoid `Any`; when an untyped provider response is unavoidable, contain it in an adapter and validate immediately. Use `Protocol` for ports, immutable dataclasses/value objects where appropriate, `NewType` or validated value objects for identifiers, and explicit `None` handling.

Use timezone-aware UTC datetimes for instants and `Decimal` for money/cost. Do not use floats for monetary values. Do not pass unstructured dictionaries across layers; define DTOs. Pattern matching or branching over unions/enums must be exhaustive and fail visibly for unknown variants.

## Docstrings and comments

Public modules, ports, non-obvious services, and reusable functions have concise docstrings describing intent, invariants, errors, and side effects. Do not restate the signature. Comments explain why a constraint exists, not what a line does. Architectural decisions and non-obvious tradeoffs belong in an ADR, not a long inline comment.

## Async and I/O

Use async only for I/O-bound boundaries and keep call chains consistently async. Never block the event loop with synchronous network, file, crypto, or database work. Apply explicit timeouts to external calls. Cancellation must propagate unless cleanup requires a brief shielded section. CPU-heavy media or AI preprocessing runs in a worker.

## Data and transactions

Application services define transaction boundaries. Repositories never commit. Workspace-owned access always includes explicit scope and active-row filtering. Mutable updates require expected `version`. ORM entities do not cross infrastructure boundaries. External calls are not made while holding long database transactions.

Use UUIDv7 where sortable identity is useful, RFC 3339 at APIs, UTC persistence, IANA zones for scheduling, and `Decimal` plus currency for money. Treat immutable records as append-only; corrections are compensating facts.

## Logging

Use the structured logging facade and event names, not string interpolation or `print`. Add useful typed fields through context. Never log tokens, passwords, authorization headers, cookies, full prompts/content, signed URLs, secret references, or unredacted provider payloads. See `LOGGING_GUIDELINES.md`.

## Exceptions

Raise the most specific domain/application exception and map it centrally at delivery boundaries. Do not raise framework HTTP exceptions from domain/application code. Never catch `Exception` merely to log and re-raise; boundary logging owns uncaught failures. Preserve causes with `raise ... from error`. Do not use exceptions for normal branching.

## File organization

One file has one stable responsibility. Keep public API near the top and private helpers below. Prefer composition over inheritance. Split files that mix transport, business policy, persistence, and provider logic or grow beyond roughly 400 cohesive lines. Avoid generic utility files.

## Security and validation

Validate every trust boundary, use allowlists for states/sorts/providers, parameterize SQL, normalize redirect URLs, and enforce authorization in the application layer. Redaction and tenant scope are explicit. Never weaken TLS, JWT verification, certificate validation, or security checks in shared production code for local convenience.

## Testing expectations

Every behavior change includes tests at the lowest sufficient level. Tests are deterministic, independent, and follow arrange/act/assert. Mock owned ports, not internal methods or third-party SDK implementation details. Time, UUIDs, and provider results are injected. Bug fixes include a regression test. See `TESTING_GUIDELINES.md`.

## Review gates

Code is not complete until formatting, lint, strict typing, relevant tests, architecture rules, migration checks, and security scans pass. Suppressions require a narrow scope and explanatory comment; blanket `noqa`, type-ignore, or coverage exclusions are prohibited.
