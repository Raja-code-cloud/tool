"""Future provider placeholder."""

from __future__ import annotations

from collections.abc import Mapping

from ..exceptions import ProviderUnavailable
from ..interfaces.identity_provider import IdentityProvider
from ..models import (
    AuthenticationResult,
    AuthorizationRequest,
    ProviderHealth,
    TokenSet,
    UserIdentity,
)
from ..utils import utc_now


class PlaceholderIdentityProvider(IdentityProvider):
    name = "placeholder"
    pkce_required = False

    @property
    def display_name(self) -> str:
        return "Future Provider"

    @property
    def authorization_base_url(self) -> str | None:
        return None

    async def authenticate(
        self, redirect_uri: str, *, scopes: tuple[str, ...] = ()
    ) -> AuthorizationRequest:
        raise ProviderUnavailable("placeholder provider is not implemented")

    async def exchange_code(
        self,
        code: str,
        redirect_uri: str,
        *,
        state: str,
        expected_state: str,
        nonce: str,
        code_verifier: str,
    ) -> AuthenticationResult:
        raise ProviderUnavailable("placeholder provider is not implemented")

    async def refresh(self, refresh_token: str) -> TokenSet:
        raise ProviderUnavailable("placeholder provider is not implemented")

    async def validate_token(self, token: str) -> AuthenticationResult:
        raise ProviderUnavailable("placeholder provider is not implemented")

    async def get_user(self, access_token: str) -> UserIdentity:
        raise ProviderUnavailable("placeholder provider is not implemented")

    async def logout(
        self, token: str | None = None, *, post_logout_redirect_uri: str | None = None
    ) -> str | None:
        raise ProviderUnavailable("placeholder provider is not implemented")

    async def health_check(self) -> ProviderHealth:
        return ProviderHealth(
            healthy=False,
            provider=self.name,
            detail="not implemented",
            checked_at=utc_now(),
        )

    def supported_scopes(self) -> frozenset[str]:
        return frozenset()

    def sanitize_claims(self, claims: Mapping[str, object]) -> Mapping[str, object]:
        return {}
