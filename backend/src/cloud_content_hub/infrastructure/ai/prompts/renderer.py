"""Strict prompt template rendering."""

from collections.abc import Mapping
from string import Formatter

from cloud_content_hub.infrastructure.ai.exceptions import AIValidationError
from cloud_content_hub.infrastructure.ai.prompts.template import PromptTemplate


def render_prompt(template: PromptTemplate, variables: Mapping[str, object]) -> str:
    fields = {name for _, name, _, _ in Formatter().parse(template.template) if name}
    required = fields | set(template.required_variables)
    missing = required - variables.keys()
    unknown = variables.keys() - fields
    if missing:
        raise AIValidationError(f"Missing prompt variables: {', '.join(sorted(missing))}")
    if unknown:
        raise AIValidationError(f"Unknown prompt variables: {', '.join(sorted(unknown))}")
    try:
        return template.template.format_map(dict(variables))
    except (KeyError, ValueError) as exc:
        raise AIValidationError("Invalid prompt template") from exc
