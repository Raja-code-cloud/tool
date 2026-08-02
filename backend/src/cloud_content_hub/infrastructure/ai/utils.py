"""Shared adapter translation helpers."""

from cloud_content_hub.infrastructure.ai.exceptions import (
    AIAuthenticationError,
    AIError,
    AIProviderError,
    AIRateLimitError,
    AITimeoutError,
    AIUnavailableError,
)


def translate_error(exc: Exception) -> AIError:
    name = type(exc).__name__.lower()
    message = str(exc) or "Provider request failed"
    if "authentication" in name or "permission" in name:
        return AIAuthenticationError("Provider authentication failed")
    if "ratelimit" in name or "resourceexhausted" in name:
        return AIRateLimitError("Provider rate limit exceeded")
    if "timeout" in name:
        return AITimeoutError("Provider request timed out")
    if "connection" in name or "unavailable" in name:
        return AIUnavailableError("Provider unavailable")
    return AIProviderError(message)
