"""Provider-neutral prompt validation."""

from cloud_content_hub.infrastructure.ai.config import ProviderConfig
from cloud_content_hub.infrastructure.ai.exceptions import PromptTooLarge, TokenLimitExceeded
from cloud_content_hub.infrastructure.ai.models import GenerationRequest, ValidationResult
from cloud_content_hub.infrastructure.ai.tokenizer import approximate_token_count


def validate_request(
    request: GenerationRequest,
    config: ProviderConfig | None = None,
) -> ValidationResult:
    errors: list[str] = []
    if not request.messages:
        errors.append("At least one message is required")
    if any(not message.content.strip() for message in request.messages):
        errors.append("Messages cannot be blank")

    estimated_tokens = approximate_token_count(request)
    safety = config.safety if config else None
    if safety:
        if safety.max_prompt_characters is not None:
            total_chars = sum(len(message.content) for message in request.messages)
            if total_chars > safety.max_prompt_characters:
                errors.append(
                    f"Prompt exceeds maximum character limit ({safety.max_prompt_characters})"
                )
        if safety.max_prompt_tokens is not None and estimated_tokens > safety.max_prompt_tokens:
            errors.append(f"Prompt exceeds maximum token limit ({safety.max_prompt_tokens})")

    return ValidationResult(
        valid=not errors,
        errors=tuple(errors),
        estimated_tokens=estimated_tokens,
    )


def ensure_valid_request(request: GenerationRequest, config: ProviderConfig | None = None) -> None:
    result = validate_request(request, config)
    if result.valid:
        return
    message = "; ".join(result.errors)
    if config and config.safety.max_prompt_tokens is not None:
        if result.estimated_tokens and result.estimated_tokens > config.safety.max_prompt_tokens:
            raise TokenLimitExceeded(message)
    if "character limit" in message or "token limit" in message:
        raise PromptTooLarge(message)
    from cloud_content_hub.infrastructure.ai.exceptions import InvalidPrompt

    raise InvalidPrompt(message)
