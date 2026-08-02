from collections.abc import Mapping
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class FieldViolation:
    field: str
    code: str
    message: str


class ApplicationError(Exception):
    default_code: ClassVar[str] = "internal_error"
    default_detail: ClassVar[str] = "An unexpected error occurred."

    def __init__(
        self,
        *,
        code: str | None = None,
        detail: str | None = None,
        parameters: Mapping[str, object] | None = None,
        errors: tuple[FieldViolation, ...] = (),
    ) -> None:
        self.code = code or self.default_code
        self.detail = detail or self.default_detail
        self.parameters = dict(parameters or {})
        self.errors = errors
        super().__init__(self.detail)


class ClientError(ApplicationError):
    default_code = "invalid_request"
    default_detail = "The request could not be processed."


class ValidationError(ClientError):
    default_code = "validation_failed"
    default_detail = "One or more fields failed validation."


class AuthenticationError(ClientError):
    default_code = "authentication_required"
    default_detail = "Authentication is required."


class AuthorizationError(ClientError):
    default_code = "permission_denied"
    default_detail = "Permission was denied."


class ResourceNotFoundError(ClientError):
    default_code = "resource_not_found"
    default_detail = "The requested resource was not found."


class ConflictError(ClientError):
    default_code = "conflict"
    default_detail = "The request conflicts with the current resource state."


class VersionConflictError(ConflictError):
    default_code = "version_conflict"
    default_detail = "The resource changed after it was loaded."


class IdempotencyConflictError(ConflictError):
    default_code = "idempotency_conflict"
    default_detail = "The idempotency key was already used with a different request."


class StateTransitionError(ConflictError):
    default_code = "invalid_state_transition"
    default_detail = "The requested state transition is not allowed."


class RateLimitError(ClientError):
    default_code = "rate_limited"
    default_detail = "Too many requests were received."


class QuotaExceededError(ClientError):
    default_code = "quota_exceeded"
    default_detail = "The applicable quota has been exceeded."


class DependencyError(ApplicationError):
    default_code = "dependency_error"
    default_detail = "A required dependency failed."


class DependencyUnavailableError(DependencyError):
    default_code = "dependency_unavailable"
    default_detail = "A required dependency is unavailable."


class DependencyTimeoutError(DependencyError):
    default_code = "dependency_timeout"
    default_detail = "A required dependency timed out."


class ProviderAuthenticationError(DependencyError):
    default_code = "provider_authentication_failed"
    default_detail = "A provider rejected service authentication."


class ProviderRateLimitError(DependencyError):
    default_code = "provider_rate_limited"
    default_detail = "A provider rate limit was reached."


class InternalError(ApplicationError):
    default_code = "internal_error"
    default_detail = "An unexpected error occurred."
