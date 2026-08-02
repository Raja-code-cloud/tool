"""Prompt template value object."""

from pydantic import BaseModel, ConfigDict


class PromptTemplate(BaseModel):
    model_config = ConfigDict(frozen=True)
    template: str
    required_variables: frozenset[str] = frozenset()
