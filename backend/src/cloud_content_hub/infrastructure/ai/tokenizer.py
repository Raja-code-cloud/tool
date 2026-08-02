"""Safe approximate tokenizer fallback."""

from cloud_content_hub.infrastructure.ai.models import GenerationRequest, Message, Role


def approximate_token_count(request: GenerationRequest) -> int:
    characters = sum(len(message.content) for message in request.messages)
    return max(1, (characters + 3) // 4)


def estimate_completion_tokens(max_tokens: int | None, default_max_tokens: int) -> int:
    return max_tokens or default_max_tokens


def build_messages(
    *,
    system: str | None = None,
    user: str | None = None,
    assistant: str | None = None,
) -> tuple[Message, ...]:
    messages: list[Message] = []
    if system:
        messages.append(Message(role=Role.SYSTEM, content=system))
    if user:
        messages.append(Message(role=Role.USER, content=user))
    if assistant:
        messages.append(Message(role=Role.ASSISTANT, content=assistant))
    return tuple(messages)
