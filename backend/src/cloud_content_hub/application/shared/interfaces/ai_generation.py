"""AI generation port for application orchestration."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ApplicationGenerationRequest:
    """Normalized generation request for the AI port."""

    model: str
    system_prompt: str
    user_prompt: str
    temperature: float | None = None
    max_tokens: int | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ApplicationGenerationResponse:
    """Normalized generation response from the AI port."""

    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    finish_reason: str | None = None
    estimated_cost: Decimal | None = None
    latency_ms: int = 0


class AIGenerationPort(Protocol):
    """Capability-oriented AI generation port."""

    async def generate(
        self, request: ApplicationGenerationRequest
    ) -> ApplicationGenerationResponse:
        """Generate content from a normalized request."""

    async def estimate_cost(self, request: ApplicationGenerationRequest) -> Decimal:
        """Estimate provider cost for a generation request."""

    async def validate_model(self, model: str) -> bool:
        """Return whether the model is enabled and available."""
