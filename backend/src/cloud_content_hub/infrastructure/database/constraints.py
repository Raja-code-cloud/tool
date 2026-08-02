"""Helpers for building deterministic SQLAlchemy check constraints."""

from cloud_content_hub.infrastructure.database.enums import DatabaseTextEnum

IMMUTABLE_UAC_CHECK: str = (
    "updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by "
    "AND deleted_at IS NULL AND version = 1"
)


def check_in(enum_cls: type[DatabaseTextEnum], *, name: str) -> str:
    """Return a SQL ``IN (...)`` expression for a text-backed enum class."""

    values = ", ".join(f"'{value}'" for value in enum_cls.values())
    return f"{name} IN ({values})"
