from celery import Celery

from cloud_content_hub.core.config import Settings, load_settings
from cloud_content_hub.core.logging import configure_logging


def create_celery_app(settings: Settings | None = None) -> Celery:
    resolved_settings = settings or load_settings()
    configure_logging(resolved_settings)
    app = Celery(
        resolved_settings.service_name,
        broker=str(resolved_settings.redis_url),
        backend=str(resolved_settings.redis_url),
    )
    app.conf.update(
        accept_content=["json"],
        task_serializer="json",
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        broker_connection_retry_on_startup=True,
    )
    return app
