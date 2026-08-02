# Providers

Adapters exist for OpenAI Responses, Azure OpenAI, Anthropic Messages, Google Gen AI, and a
deterministic mock. Vendor exceptions are translated to the local AI exception vocabulary.
Pricing is deliberately configured through `PricingCatalog`; prices change and are not hardcoded.
Token counting uses a conservative provider-neutral estimate unless an adapter supplies an exact
count. No adapter logs prompts, generated content, raw payloads, credentials, or headers.
