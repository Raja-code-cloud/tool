"""Analytics-specific application exceptions."""

from cloud_content_hub.core.errors import ClientError, ValidationError


class AnalyticsNotFoundError(ClientError):
    default_code = "resource_not_found"
    default_detail = "The requested analytics resource was not found."


class AnalyticsValidationError(ValidationError):
    default_code = "validation_failed"
    default_detail = "The analytics request failed validation."


class AnalyticsExportLimitError(ValidationError):
    default_code = "validation_failed"
    default_detail = "The analytics export request exceeds allowed limits."


class AnalyticsPlatformError(ValidationError):
    default_code = "validation_failed"
    default_detail = "One or more platform identifiers are invalid for this workspace."


class AnalyticsMetricError(ValidationError):
    default_code = "validation_failed"
    default_detail = "One or more metric codes are not recognized."


class AnalyticsSnapshotNotFoundError(ClientError):
    default_code = "resource_not_found"
    default_detail = "The requested analytics snapshot was not found."
