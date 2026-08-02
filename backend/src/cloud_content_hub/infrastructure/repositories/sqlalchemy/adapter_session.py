"""Session access helpers for SQLAlchemy repository adapters."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.infrastructure.repositories.sqlalchemy.unit_of_work import (
    SqlAlchemyUnitOfWork,
)


def resolve_session(unit_of_work: IUnitOfWork) -> AsyncSession:
    """Return the active SQLAlchemy session owned by the unit of work."""

    if isinstance(unit_of_work, SqlAlchemyUnitOfWork):
        return unit_of_work.session
    session = getattr(unit_of_work, "session", None)
    if session is None or not isinstance(session, AsyncSession):
        msg = "Unit of work does not expose an active SQLAlchemy session."
        raise RuntimeError(msg)
    return session
