# Prompt Layer

Generic prompt utilities live in `infrastructure/ai/prompts/`. They contain no product or
business-specific templates.

## Template rendering

`PromptTemplate` wraps a Python format string. `render_prompt()` performs strict substitution:

- missing variables raise `AIValidationError`
- unknown variables raise `AIValidationError`
- `required_variables` can declare placeholders not inferred from the template

## Message construction

`tokenizer.build_messages()` creates normalized `Message` tuples:

```python
build_messages(system="You are helpful.", user="Summarize this.")
```

Roles map to `Role.SYSTEM`, `Role.USER`, and `Role.ASSISTANT`.

## Validation

`prompts/validators.py` validates `GenerationRequest` instances:

- at least one non-blank message
- optional size limits from `SafetyConfig`:
  - `max_prompt_characters`
  - `max_prompt_tokens` (estimated)

Violations return `ValidationResult` or raise `InvalidPrompt`, `PromptTooLarge`, or
`TokenLimitExceeded` via `ensure_valid_request()`.

## Metadata

`PromptMetadata` captures name, version, tags, and source for tracing. It is attached to
requests and must never contain secrets or raw customer content in logs.

## Limits

Prompt size enforcement is configuration-driven. Adapters call shared validation through
`ProviderSupport.validate_prompt()` so limits are consistent across vendors.
