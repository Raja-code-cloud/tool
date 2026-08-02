# AI testing

Unit and contract tests use `MockProvider`; no test requires a live account or network. Tests cover
strict template rendering, prompt validation, retry, pricing, generation, normalized streaming,
factory construction, fallback, capabilities, telemetry redaction, usage ledger, and future
placeholder registration.

## Commands

```bash
cd backend
set PYTHONPATH=src
pytest tests/unit/test_ai.py tests/contract/test_ai_provider_contract.py -v
```

## Fixtures and fakes

- `MockProvider`: deterministic responses, optional `fail = True`
- `FailingMockProvider`: always unhealthy/unavailable
- `RateLimitedMockProvider`: simulates transient failure then success

## Contract suite

`tests/contract/test_ai_provider_contract.py` verifies every adapter satisfies `AIProvider` without
network access. Add new providers to this suite when registering adapters.

## Guidelines

- Mock owned ports, not SDK internals.
- Never assert on prompt/content in telemetry tests; verify redaction only.
- Inject clocks and retry policies with zero delay in unit tests.
