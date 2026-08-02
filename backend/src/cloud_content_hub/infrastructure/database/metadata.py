"""Shared SQLAlchemy metadata."""

from sqlalchemy import MetaData

from cloud_content_hub.infrastructure.database.naming import NAMING_CONVENTION

metadata = MetaData(naming_convention=NAMING_CONVENTION)
"""Metadata shared by every mapped table and Alembic."""
