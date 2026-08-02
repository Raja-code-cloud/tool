"""Provider-neutral asynchronous identity provider contract."""

from abc import ABC, abstractmethod
from collections.abc import Mapping

from ..models import (
    AuthenticationResult,
    AuthorizationRequest,
    ProviderHealth,
    TokenSet,
    UserIdentity,
)


class IdentityProvider(ABC):
    name: str
    pkce_required: bool = True

    @property
    @abstractmethod
    def display_name(self) -> str: ...

    @property
    @abstractmethod
    def authorization_base_url(self) -> str | None: ...

    @abstractmethod
    async def authenticate(
        self, redirect_uri: str, *, scopes: tuple[str, ...] = ()
    ) -> AuthorizationRequest: ...

    @abstractmethod
    async def exchange_code(
        self,
        code: str,
        redirect_uri: str,
        *,
        state: str,
        expected_state: str,
        nonce: str,
        code_verifier: str,
    ) -> AuthenticationResult: ...

    @abstractmethod
    async def refresh(self, refresh_token: str) -> TokenSet: ...

    @abstractmethod
    async def validate_token(self, token: str) -> AuthenticationResult: ...

    @abstractmethod
    async def get_user(self, access_token: str) -> UserIdentity: ...

    @abstractmethod
    async def logout(
        self, token: str | None = None, *, post_logout_redirect_uri: str | None = None
    ) -> str | None: ...

    @abstractmethod
    async def health_check(self) -> ProviderHealth: ...

    @abstractmethod
    def supported_scopes(self) -> frozenset[str]: ...

    def sanitize_claims(self, claims: Mapping[str, object]) -> Mapping[str, object]:
        """Providers map raw claims internally; callers never receive them."""
        raise NotImplementedError
