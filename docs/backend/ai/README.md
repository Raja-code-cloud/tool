# AI provider layer

The AI infrastructure exposes an async, SDK-free `AIProvider` protocol and normalized request,
response, stream, health, capability, and usage models. Application code receives `AIClient` or
`AIProvider` by dependency injection and never imports vendor SDKs.

Providers are created only through `create_provider`. New adapters register a builder in a
`ProviderRegistry`; existing adapters do not need modification. `AIClient` performs health-aware
fallback, retries transient failures, invokes safety and circuit-breaker hooks, and normalizes
failures to local exceptions.

## Documentation index

| Document                                         | Topic                            |
| ------------------------------------------------ | -------------------------------- |
| [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)         | Layer layout and lifecycle       |
| [PROVIDER_INTERFACE.md](PROVIDER_INTERFACE.md)   | Contract, models, construction   |
| [SUPPORTED_PROVIDERS.md](SUPPORTED_PROVIDERS.md) | Vendor adapters and extension    |
| [CONFIGURATION.md](CONFIGURATION.md)             | Typed settings                   |
| [PROMPT_LAYER.md](PROMPT_LAYER.md)               | Templates and validation         |
| [TOKEN_ACCOUNTING.md](TOKEN_ACCOUNTING.md)       | Estimation and usage ledger      |
| [COST_ESTIMATION.md](COST_ESTIMATION.md)         | Pricing catalog                  |
| [STREAMING.md](STREAMING.md)                     | Async streaming behavior         |
| [FAILOVER_STRATEGY.md](FAILOVER_STRATEGY.md)     | Retries, fallback, circuit hooks |
| [HEALTH_CHECKS.md](HEALTH_CHECKS.md)             | Provider probes                  |
| [TESTING.md](TESTING.md)                         | Mock provider and test commands  |

## Package location

```text
backend/src/cloud_content_hub/infrastructure/ai/
```

This follows the canonical backend folder structure documented in `FOLDER_STRUCTURE.md`.
