from sqlalchemy.orm import DeclarativeBase

from cloud_content_hub.infrastructure.database.metadata import metadata


class Base(DeclarativeBase):
    """Root for all SQLAlchemy declarative models.

    Identity is deliberately not defined here: most tables use ``id``, while
    junction tables use composite keys and asset subtype tables use
    ``asset_id`` as their primary key.
    """

    metadata = metadata
