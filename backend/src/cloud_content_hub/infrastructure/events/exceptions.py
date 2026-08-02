"""Stable event publishing failure vocabulary."""


class EventError(Exception):
    """Base class for event infrastructure failures."""


class EventSerializationError(EventError):
    """Raised when a domain event cannot be serialized safely."""


class UnknownEventTypeError(EventError):
    """Raised when an event type is not registered."""


class OutboxWriteError(EventError):
    """Raised when an outbox append fails."""


class OutboxDispatchError(EventError):
    """Raised when dispatching an outbox event fails."""


class PoisonMessageError(OutboxDispatchError):
    """Raised when an event is classified as non-retryable poison."""


class OutboxRetryExhaustedError(OutboxDispatchError):
    """Raised when retry attempts are exhausted for an outbox event."""
