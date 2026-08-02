"""Small safety utilities shared by observability adapters."""

import re
from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

_SAFE_ROUTE: Final = re.compile(r"^/[A-Za-z0-9_{}./:-]{0,255}$")
_SECRET_KEYS: Final = re.compile(
    r"(authorization|cookie|password|secret|token|api[_-]?key|connection[_-]?string|prompt)",
    re.IGNORECASE,
)


def safe_route_label(scope: Mapping[str, object]) -> str:
    """Return a bounded route template, never a raw high-cardinality URL."""
    route = scope.get("route")
    path = getattr(route, "path", None)
    if isinstance(path, str) and _SAFE_ROUTE.fullmatch(path):
        return path
    return "unmatched"


def redact_mapping(
    values: Mapping[str, object],
    *,
    allowed_keys: frozenset[str] | None = None,
) -> Mapping[str, object]:
    """Create an immutable, shallow, fail-closed redacted mapping."""
    clean: dict[str, object] = {}
    for key, value in values.items():
        if allowed_keys is not None and key not in allowed_keys:
            continue
        clean[key] = "[REDACTED]" if _SECRET_KEYS.search(key) else _safe_scalar(value)
    return MappingProxyType(clean)


def _safe_scalar(value: object) -> object:
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value[:1024]
    return f"<{type(value).__name__}>"
