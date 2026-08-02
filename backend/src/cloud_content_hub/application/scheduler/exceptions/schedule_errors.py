"""Scheduler-specific application exceptions."""

from cloud_content_hub.core.errors import ClientError, ConflictError


class ScheduleNotFoundError(ClientError):
    default_code = "resource_not_found"
    default_detail = "The requested schedule was not found."


class ScheduleTimeNonexistentError(ClientError):
    default_code = "schedule_time_nonexistent"
    default_detail = "The requested local time does not exist in the given time zone."


class ScheduleTimeAmbiguousError(ConflictError):
    default_code = "schedule_time_ambiguous"
    default_detail = "The requested local time is ambiguous; fold or ambiguity policy is required."
