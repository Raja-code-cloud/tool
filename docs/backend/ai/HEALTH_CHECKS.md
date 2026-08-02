# Health Checks

Each adapter implements `health_check() -> HealthStatus`.

## HealthStatus fields

| Field              | Meaning                                         |
| ------------------ | ----------------------------------------------- |
| `healthy`          | Whether the adapter is ready to serve traffic   |
| `latency_ms`       | Round-trip time of the probe                    |
| `detail`           | Safe diagnostic text (no secrets)               |
| `available_models` | Models reported or configured for this instance |

## Probe strategies

| Provider     | Probe                                    |
| ------------ | ---------------------------------------- |
| OpenAI       | `models.list()`                          |
| Azure OpenAI | Same as OpenAI via Azure client          |
| Claude       | `models.list()`                          |
| Gemini       | `models.get(model)` for configured model |
| Mock         | Local flag (`fail`) without network      |

Shared helper `timed_health_check()` in `providers/base.py` measures latency and normalizes
failures.

## Client integration

`AIClient` calls `health_check()` before `generate()` and `stream()`. Unhealthy providers are
skipped automatically; they do not block fallback candidates.

## Readiness vs liveness

- **Liveness**: process can execute Python and schedule tasks.
- **Readiness**: at least one configured provider passes `health_check()` when AI features are
  required.

Expose readiness through the operations layer; this module only defines provider-level probes.

## Security

Health endpoints and logs must not return API keys, prompts, or raw vendor error bodies.
