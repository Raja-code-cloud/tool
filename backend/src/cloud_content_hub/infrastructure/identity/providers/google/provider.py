"""Google OAuth 2.0 identity provider."""

from __future__ import annotations

from ...config import IdentitySettings
from ...jwt import JwtService
from ...tokens import TokenService
from ..base_oauth import BaseOAuthProvider


class GoogleIdentityProvider(BaseOAuthProvider):
    name = "google"

    def __init__(
        self,
        settings: IdentitySettings,
        jwt_service: JwtService,
        token_service: TokenService,
    ) -> None:
        super().__init__(settings, jwt_service, token_service)
        if not settings.google_client_id:
            raise ValueError("google provider requires client_id")

    @property
    def display_name(self) -> str:
        return "Google"

    @property
    def client_id(self) -> str:
        return self._settings.google_client_id or ""

    @property
    def client_secret(self) -> str | None:
        return self._settings.google_client_secret

    @property
    def redirect_uris(self) -> tuple[str, ...]:
        return self._settings.google_redirect_uris

    @property
    def default_scopes(self) -> tuple[str, ...]:
        return self._settings.google_scopes

    @property
    def authorization_endpoint(self) -> str:
        return "https://accounts.google.com/o/oauth2/v2/auth"

    @property
    def token_endpoint(self) -> str:
        return "https://oauth2.googleapis.com/token"

    @property
    def jwks_url(self) -> str:
        return self._settings.google_jwks_url

    @property
    def issuer(self) -> str:
        return self._settings.google_authority

    def supported_scopes(self) -> frozenset[str]:
        return frozenset(self._settings.google_scopes)
