"""Stable provider-neutral AI failure vocabulary."""


class AIError(Exception):
    """Base exception for all AI infrastructure failures."""


class AIConfigurationError(AIError):
    """Invalid or incomplete AI provider configuration."""


class AIValidationError(AIError):
    """Prompt or request validation failed."""


class InvalidPrompt(AIValidationError):
    """Prompt content or structure is invalid."""


class PromptTooLarge(AIValidationError):
    """Prompt exceeds configured size limits."""


class AIAuthenticationError(AIError):
    """Provider authentication failed."""


class AuthenticationFailed(AIAuthenticationError):
    """Alias for provider authentication failures."""


class AIRateLimitError(AIError):
    """Provider rate limit exceeded."""


class RateLimitExceeded(AIRateLimitError):
    """Alias for rate limit failures."""


class AITimeoutError(AIError):
    """Provider request timed out."""


class AIUnavailableError(AIError):
    """Provider is unavailable or unreachable."""


class ProviderUnavailable(AIUnavailableError):
    """Alias for provider unavailability."""


class AIProviderError(AIError):
    """Generic provider request failure."""


class AIProviderException(AIProviderError):
    """Alias for generic provider failures."""


class GenerationFailed(AIProviderError):
    """Text generation failed after retries."""


class StreamingFailed(AIProviderError):
    """Streaming generation failed."""


class ModelNotSupported(AIConfigurationError):
    """Requested model is not supported by the provider."""


class TokenLimitExceeded(AIValidationError):
    """Token count exceeds model or request limits."""


class AICircuitOpenError(AIUnavailableError):
    """Circuit breaker is open for the provider."""
