"""Microsoft Entra ID identity provider."""

from __future__ import annotations

from ...config import IdentitySettings
from ...jwt import JwtService
from ...tokens import TokenService
from ..base_oauth import BaseOAuthProvider


class EntraIdentityProvider(BaseOAuthProvider):
    name = "entra"

    def __init__(
        self,
        settings: IdentitySettings,
        jwt_service: JwtService,
        token_service: TokenService,
    ) -> None:
        super().__init__(settings, jwt_service, token_service)
        if not settings.entra_client_id or not settings.entra_tenant_id:
            raise ValueError("entra provider requires client_id and tenant_id")

    @property
    def display_name(self) -> str:
        return "Microsoft Entra ID"

    @property
    def client_id(self) -> str:
        return self._settings.entra_client_id or ""

    @property
    def client_secret(self) -> str | None:
        return self._settings.entra_client_secret

    @property
    def redirect_uris(self) -> tuple[str, ...]:
        return self._settings.entra_redirect_uris

    @property
    def default_scopes(self) -> tuple[str, ...]:
        return self._settings.entra_scopes

    @property
    def authorization_endpoint(self) -> str:
        return f"{self._settings.entra_authority_url()}/oauth2/v2.0/authorize"

    @property
    def token_endpoint(self) -> str:
        return f"{self._settings.entra_authority_url()}/oauth2/v2.0/token"

    @property
    def jwks_url(self) -> str:
        return self._settings.entra_jwks_uri()

    @property
    def issuer(self) -> str:
        return f"https://login.microsoftonline.com/{self._settings.entra_tenant_id}/v2.0"

    def supported_scopes(self) -> frozenset[str]:
        return frozenset(self._settings.entra_scopes)
