"""Local mock identity provider for development and testing."""

from __future__ import annotations

import secrets
from collections.abc import Mapping
from urllib.parse import urlencode

from ...claims import to_unified_identity, to_user_identity
from ...config import IdentitySettings
from ...exceptions import OAuthValidationError
from ...interfaces.identity_provider import IdentityProvider
from ...jwt import JwtService
from ...logging import log_auth_failure, log_auth_success
from ...models import (
    AuthenticationResult,
    AuthorizationRequest,
    IdentityClaims,
    ProviderHealth,
    TokenSet,
    TokenType,
    UserIdentity,
)
from ...oauth import OAuthFlowManager
from ...tokens import TokenService
from ...utils import utc_now
from ...validators import validate_redirect_uri, validate_state


class MockIdentityProvider(IdentityProvider):
    name = "mock"
    pkce_required = True

    def __init__(
        self,
        settings: IdentitySettings,
        jwt_service: JwtService,
        token_service: TokenService,
    ) -> None:
        self._settings = settings
        self._jwt = jwt_service
        self._tokens = token_service
        self._oauth = OAuthFlowManager()
        self._sessions: dict[str, str] = {}

    @property
    def display_name(self) -> str:
        return "Mock Provider"

    @property
    def authorization_base_url(self) -> str | None:
        return "mock://authorize"

    async def authenticate(
        self, redirect_uri: str, *, scopes: tuple[str, ...] = ()
    ) -> AuthorizationRequest:
        validate_redirect_uri(
            redirect_uri,
            allowed=self._settings.mock_redirect_uris,
            https_only=False,
        )
        session = self._oauth.begin(redirect_uri)
        self._sessions[session.state] = session.nonce
        params = {
            "state": session.state,
            "nonce": session.nonce,
            "redirect_uri": redirect_uri,
            "code_challenge": session.code_challenge,
        }
        return AuthorizationRequest(
            url=f"mock://authorize?{urlencode(params)}",
            state=session.state,
            nonce=session.nonce,
            code_verifier=session.code_verifier,
            code_challenge=session.code_challenge,
            provider=self.name,
        )

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
        started = utc_now()
        try:
            validate_state(state, expected_state)
            if not code.startswith("mock-"):
                raise OAuthValidationError("invalid mock authorization code")
            subject = code.removeprefix("mock-")
            unified = to_unified_identity(
                IdentityClaims(
                    subject=subject,
                    issuer=self._settings.issuer,
                    audience=(self._settings.audience,),
                    expires_at=utc_now(),
                    email=f"{subject}@example.test",
                    name=f"Mock {subject.title()}",
                    roles=frozenset({"user"}),
                    permissions=frozenset({"profile:read"}),
                    provider=self.name,
                )
            )
            session = await self._tokens.issue_session(unified)
            claims = IdentityClaims(
                subject=unified.subject,
                issuer=self._settings.issuer,
                audience=(self._settings.audience,),
                expires_at=utc_now(),
                email=unified.email,
                name=unified.display_name,
                roles=unified.roles,
                permissions=unified.permissions,
                provider=self.name,
                token_id=session.token_id,
                token_type=TokenType.ACCESS,
            )
            user = to_user_identity(claims)
            log_auth_success(provider=self.name, subject=user.subject, started_at=started)
            return AuthenticationResult(
                user=user,
                claims=claims,
                tokens=TokenSet(
                    access_token=session.access_token,
                    refresh_token=session.refresh_token,
                    expires_in=session.expires_in,
                ),
                unified=unified,
            )
        except Exception as error:
            log_auth_failure(
                provider=self.name,
                reason=error.__class__.__name__,
                started_at=started,
            )
            raise

    async def refresh(self, refresh_token: str) -> TokenSet:
        return await self._tokens.refresh_access_token(refresh_token)

    async def validate_token(self, token: str) -> AuthenticationResult:
        decoded = await self._jwt.decode_and_verify(token, token_type=TokenType.ACCESS)
        user = to_user_identity(decoded.claims)
        return AuthenticationResult(
            user=user,
            claims=decoded.claims,
            unified=to_unified_identity(decoded.claims),
        )

    async def get_user(self, access_token: str) -> UserIdentity:
        return (await self.validate_token(access_token)).user

    async def logout(
        self, token: str | None = None, *, post_logout_redirect_uri: str | None = None
    ) -> str | None:
        if token is not None:
            await self._tokens.revoke_refresh_token(token)
        return post_logout_redirect_uri

    async def health_check(self) -> ProviderHealth:
        return ProviderHealth(healthy=True, provider=self.name, checked_at=utc_now())

    def supported_scopes(self) -> frozenset[str]:
        return frozenset({"openid", "profile", "email"})

    def sanitize_claims(self, claims: Mapping[str, object]) -> Mapping[str, object]:
        return dict(claims)

    def issue_mock_code(self, subject: str | None = None) -> str:
        return f"mock-{subject or secrets.token_hex(8)}"
