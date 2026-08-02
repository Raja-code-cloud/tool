"""Analytics repository and provider ports."""

from cloud_content_hub.application.analytics.interfaces.analytics_repository import (
    IAnalyticsRepository,
)
from cloud_content_hub.application.analytics.interfaces.event_publisher import (
    IAnalyticsEventPublisher,
)

__all__ = ["IAnalyticsEventPublisher", "IAnalyticsRepository"]
