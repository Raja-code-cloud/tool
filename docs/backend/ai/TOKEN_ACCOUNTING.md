# Token Accounting

Token utilities provide provider-independent estimation and per-process usage tracking.

## Estimation (`tokenizer.py`)

`approximate_token_count(request)` uses a conservative character-based heuristic
(`ceil(chars / 4)`). Adapters may override with vendor-specific counting when available.

`estimate_completion_tokens()` resolves output budget from request override or provider
defaults.

## Usage ledger (`usage.py`)

`UsageLedger` records cumulative `TokenUsage` per provider name inside a process. It is
async-safe and intended for diagnostics, rate-limit observability, and tests.

`AIClient` optionally accepts a ledger and records usage after successful generations.

## Validation integration

`ValidationResult.estimated_tokens` exposes the pre-call estimate during prompt validation.

## Reporting

Application layers should persist authoritative usage from `GenerationResponse.usage` to the
database. The ledger is not durable storage.

## Guidelines

- Never log full prompts or completions when reporting usage.
- Prefer normalized `TokenUsage` over vendor-specific field names at application boundaries.
