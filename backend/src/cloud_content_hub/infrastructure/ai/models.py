"""Provider-neutral AI value objects."""

from collections.abc import Mapping
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

JsonValue = Any


class Capability(StrEnum):
    TEXT = "text"
    STREAMING = "streaming"
    JSON = "json"
    TOOLS = "tools"
    VISION = "vision"


class Role(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class FinishReason(StrEnum):
    STOP = "stop"
    LENGTH = "length"
    CONTENT_FILTER = "content_filter"
    TOOL_CALL = "tool_call"
    ERROR = "error"
    UNKNOWN = "unknown"


class Message(BaseModel):
    model_config = ConfigDict(frozen=True)

    role: Role
    content: str


class PromptMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str | None = None
    version: str | None = None
    tags: frozenset[str] = frozenset()
    source: str | None = None


class GenerationRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    messages: tuple[Message, ...]
    model: str | None = None
    temperature: float | None = Field(default=None, ge=0, le=2)
    max_tokens: int | None = Field(default=None, gt=0)
    stream: bool | None = None
    metadata: Mapping[str, str] = Field(default_factory=dict)
    prompt_metadata: PromptMetadata | None = None


class TokenUsage(BaseModel):
    model_config = ConfigDict(frozen=True)

    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class GenerationResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    content: str
    model: str
    provider: str
    usage: TokenUsage
    finish_reason: str | None = None
    request_id: str | None = None
    estimated_cost: Decimal | None = None
    latency_ms: int = Field(default=0, ge=0)
    metadata: Mapping[str, str] = Field(default_factory=dict)


class StreamChunk(BaseModel):
    model_config = ConfigDict(frozen=True)

    content: str = ""
    model: str
    provider: str
    finish_reason: str | None = None
    usage: TokenUsage | None = None
    estimated_cost: Decimal | None = None
    metadata: Mapping[str, str] = Field(default_factory=dict)


class HealthStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    healthy: bool
    latency_ms: int = Field(ge=0)
    detail: str = ""
    available_models: tuple[str, ...] = ()


class ValidationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    valid: bool
    errors: tuple[str, ...] = ()
    estimated_tokens: int | None = None
