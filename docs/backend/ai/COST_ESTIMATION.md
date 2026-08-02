# Cost Estimation

Costs are computed through `PricingCatalog` in `cost.py`. Prices are configuration data, not
hardcoded constants, so operations can update pricing without code changes.

## Model pricing

Register per provider/model pair:

```python
catalog.register(
    "openai",
    "gpt-4.1",
    ModelPricing(input_per_million=Decimal("2.0"), output_per_million=Decimal("8.0")),
)
```

## Estimation

`PricingCatalog.estimate(provider, model, usage)` returns total cost as `Decimal`:

```text
(input_tokens * input_rate + output_tokens * output_rate) / 1_000_000
```

Missing pricing raises `AIConfigurationError`.

## Adapter integration

Pass `pricing_catalog` when constructing providers or use `ProviderSupport.attach_cost()` to
populate `GenerationResponse.estimated_cost` after generation.

`AIClient` logs stringified estimated cost through metadata-only telemetry.

## Pre-call estimates

`AIProvider.estimate_cost(request)` combines prompt token estimate with configured output
budget to approximate worst-case spend before calling the vendor.

## Money handling

All monetary values use `Decimal`, never binary floats, per backend coding standards.
