"""Reusable AI test fakes."""

from cloud_content_hub.infrastructure.ai.exceptions import AIUnavailableError
from cloud_content_hub.infrastructure.ai.providers.mock_provider import MockProvider


class FailingMockProvider(MockProvider):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]
        self.fail = True


class RateLimitedMockProvider(MockProvider):
    attempts = 0

    async def generate(self, request):  # type: ignore[no-untyped-def]
        self.attempts += 1
        if self.attempts == 1:
            raise AIUnavailableError("transient")
        return await super().generate(request)
