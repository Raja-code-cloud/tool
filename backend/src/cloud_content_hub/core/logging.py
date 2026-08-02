import logging
import sys
from collections.abc import MutableMapping
from typing import Any, cast

import structlog

from cloud_content_hub.core.config import Settings
from cloud_content_hub.core.context import correlation_id_var, request_id_var


def add_context(
    _logger: Any, _method_name: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    if request_id := request_id_var.get():
        event_dict["request_id"] = request_id
    if correlation_id := correlation_id_var.get():
        event_dict["correlation_id"] = correlation_id
    return event_dict


def configure_logging(settings: Settings) -> None:
    def add_service_context(
        _logger: object,
        _method_name: str,
        event_dict: MutableMapping[str, Any],
    ) -> MutableMapping[str, Any]:
        event_dict["service"] = settings.service_name
        event_dict["environment"] = settings.environment.value
        event_dict["version"] = settings.service_version
        return event_dict

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.log_level.upper(),
        force=True,
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_service_context,
            add_context,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level.upper())
        ),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger() -> structlog.stdlib.BoundLogger:
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger())
