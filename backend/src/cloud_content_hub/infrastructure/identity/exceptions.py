"""Identity errors safe for transport-layer translation."""


class IdentityError(Exception):
    """Base class for identity infrastructure failures."""


class AuthenticationException(IdentityError):
    """Authentication could not be established."""


class AuthorizationException(IdentityError):
    """Authenticated principal lacks required access."""


AuthenticationError = AuthenticationException
AuthorizationError = AuthorizationException


class TokenExpired(AuthenticationException):
    """Token has expired."""


class InvalidToken(AuthenticationException):
    """Token is malformed or fails validation."""


class MissingToken(AuthenticationException):
    """Required bearer token was not supplied."""


class TokenValidationError(InvalidToken):
    """Token failed cryptographic or semantic validation."""


class OAuthValidationError(AuthenticationException):
    """OAuth state, nonce, or callback validation failed."""


class OAuthExchangeFailed(AuthenticationException):
    """Authorization code exchange with the provider failed."""


class ProviderUnavailable(IdentityError):
    """Identity provider is unreachable or unhealthy."""


ProviderUnavailableError = ProviderUnavailable


class PermissionDenied(AuthorizationException):
    """Principal lacks the required permission."""


class RoleDenied(AuthorizationException):
    """Principal lacks the required role."""


class IdentityResolutionFailed(AuthenticationException):
    """External identity could not be resolved to a principal."""


class ConfigurationError(IdentityError):
    """Identity configuration is invalid or incomplete."""
