"""Deterministic SQL identifier conventions."""

from typing import Final

from sqlalchemy.sql.schema import Constraint

POSTGRESQL_IDENTIFIER_LIMIT: Final = 63

NAMING_CONVENTION: Final[dict[str, str]] = {
    "ix": "ix_%(table_name)s__%(column_0_N_name)s",
    "uq": "uq_%(table_name)s__%(column_0_N_name)s",
    "ck": "ck_%(table_name)s__%(constraint_name)s",
    "fk": "fk_%(table_name)s__%(column_0_N_name)s__%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


def check_name(table_name: str, rule: str) -> str:
    """Return an explicit check-constraint name validated for PostgreSQL."""

    return _validated_name(f"ck_{table_name}__{rule}")


def exclusion_name(table_name: str, rule: str) -> str:
    """Return an explicit exclusion-constraint name validated for PostgreSQL."""

    return _validated_name(f"ex_{table_name}__{rule}")


def trigger_name(table_name: str, action: str) -> str:
    """Return a deterministic trigger name validated for PostgreSQL."""

    return _validated_name(f"trg_{table_name}__{action}")


def rendered_constraint_name(constraint: Constraint) -> str:
    """Return a concrete generated constraint name for diagnostics and tests."""

    if constraint.name is None:
        msg = "constraint is not attached to named metadata"
        raise ValueError(msg)
    return str(constraint.name)


def _validated_name(name: str) -> str:
    if len(name.encode("utf-8")) > POSTGRESQL_IDENTIFIER_LIMIT:
        msg = f"PostgreSQL identifier exceeds {POSTGRESQL_IDENTIFIER_LIMIT} bytes: {name}"
        raise ValueError(msg)
    return name
