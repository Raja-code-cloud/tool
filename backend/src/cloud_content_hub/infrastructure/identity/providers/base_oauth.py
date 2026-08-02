"""Shared OAuth provider behavior."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from urllib.parse import urlencode

from ..claims import to_unified_identity, to_user_identity
from ..config import IdentitySettings
from ..exceptions import OAuthExchangeFailed
from ..interfaces.identity_provider import IdentityProvider
from ..jwt import JwtService
from ..logging import log_auth_failure, log_auth_success
from ..models import (
    AuthenticationResult,
    AuthorizationRequest,
    IdentityClaims,
    ProviderHealth,
    TokenSet,
    TokenType,
    UserIdentity,
)
from ..oauth import OAuthFlowManager, build_oauth_client
from ..tokens import TokenService
from ..utils import utc_now
from ..validators import (
    validate_authorization_code,
    validate_code_verifier,
    validate_nonce,
    validate_redirect_uri,
    validate_state,
)


class BaseOAuthProvider(IdentityProvider, ABC):
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

    @property
    @abstractmethod
    def client_id(self) -> str: ...

    @property
    @abstractmethod
    def client_secret(self) -> str | None: ...

    @property
    @abstractmethod
    def redirect_uris(self) -> tuple[str, ...]: ...

    @property
    @abstractmethod
    def default_scopes(self) -> tuple[str, ...]: ...

    @property
    @abstractmethod
    def authorization_endpoint(self) -> str: ...

    @property
    @abstractmethod
    def token_endpoint(self) -> str: ...

    @property
    @abstractmethod
    def jwks_url(self) -> str: ...

    @property
    @abstractmethod
    def issuer(self) -> str: ...

    @property
    def authorization_base_url(self) -> str | None:
        return self.authorization_endpoint

    async def authenticate(
        self, redirect_uri: str, *, scopes: tuple[str, ...] = ()
    ) -> AuthorizationRequest:
        validate_redirect_uri(
            redirect_uri,
            allowed=self.redirect_uris,
            https_only=self._settings.https_only and self._settings.environment.lower() != "local",
        )
        session = self._oauth.begin(redirect_uri)
        effective_scopes = scopes or self.default_scopes
        url = self.build_authorization_url(
            redirect_uri=redirect_uri,
            state=session.state,
            nonce=session.nonce,
            code_challenge=session.code_challenge,
            scopes=effective_scopes,
        )
        return self._oauth.to_authorization_request(
            session,
            authorization_url=url,
            provider=self.name,
        )

    def build_authorization_url(
        self,
        *,
        redirect_uri: str,
        state: str,
        nonce: str,
        code_challenge: str,
        scopes: tuple[str, ...],
    ) -> str:
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
            "nonce": nonce,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        return f"{self.authorization_endpoint}?{urlencode(params)}"

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
            validate_authorization_code(code)
            validate_state(state, expected_state)
            validate_code_verifier(code_verifier)
            validate_redirect_uri(
                redirect_uri,
                allowed=self.redirect_uris,
                https_only=self._settings.https_only
                and self._settings.environment.lower() != "local",
            )
            token_set = await self._exchange_authorization_code(
                code, redirect_uri, code_verifier=code_verifier
            )
            id_token = token_set.id_token
            if id_token is None:
                raise OAuthExchangeFailed("provider did not return an id_token")
            unified = await self._jwt.verify_external_token(
                id_token,
                jwks_url=self.jwks_url,
                issuer=self.issuer,
                audience=self.client_id,
                provider=self.name,
            )
            validate_nonce(self._extract_nonce(id_token), nonce)
            session = await self._tokens.issue_session(unified)
            claims = IdentityClaims(
                subject=unified.subject,
                issuer=self.issuer,
                audience=(self.client_id,),
                expires_at=utc_now(),
                email=unified.email,
                name=unified.display_name,
                tenant_id=unified.tenant_id,
                roles=unified.roles,
                groups=unified.groups,
                permissions=unified.permissions,
                provider=unified.provider,
                profile_picture=unified.profile_picture,
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
                    id_token=id_token,
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

    def sanitize_claims(self, claims: Mapping[str, object]) -> Mapping[str, object]:
        blocked = {"password", "client_secret", "refresh_token", "access_token"}
        return {key: value for key, value in claims.items() if key not in blocked}

    async def health_check(self) -> ProviderHealth:
        from ..jwt import JwksHealthChecker

        checker = JwksHealthChecker()
        jwks_ok = await checker.check(self.jwks_url)
        return ProviderHealth(
            healthy=jwks_ok,
            provider=self.name,
            detail="ok" if jwks_ok else "jwks unavailable",
            checked_at=utc_now(),
            jwks_available=jwks_ok,
            issuer_valid=True,
        )

    def _extract_nonce(self, id_token: str) -> str | None:
        payload = self._jwt.decode_unverified(id_token)
        nonce = payload.get("nonce")
        return str(nonce) if nonce is not None else None

    async def _exchange_authorization_code(
        self, code: str, redirect_uri: str, *, code_verifier: str
    ) -> TokenSet:
        client = build_oauth_client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=redirect_uri,
            scope=self.default_scopes,
            token_endpoint=self.token_endpoint,
        )
        try:
            token_response = await client.fetch_token(
                self.token_endpoint,
                code=code,
                code_verifier=code_verifier,
            )
        except Exception as error:
            raise OAuthExchangeFailed("authorization code exchange failed") from error
        return TokenSet(
            access_token=str(token_response["access_token"]),
            refresh_token=token_response.get("refresh_token"),
            id_token=token_response.get("id_token"),
            expires_in=token_response.get("expires_in"),
            scope=tuple(str(token_response.get("scope", "")).split()),
        )

    async def refresh(self, refresh_token: str) -> TokenSet:
        return await self._tokens.refresh_access_token(refresh_token)

    async def validate_token(self, token: str) -> AuthenticationResult:
        decoded = await self._jwt.decode_and_verify(token, token_type=TokenType.ACCESS)
        user = to_user_identity(decoded.claims)
        unified = to_unified_identity(decoded.claims)
        return AuthenticationResult(user=user, claims=decoded.claims, unified=unified)

    async def get_user(self, access_token: str) -> UserIdentity:
        result = await self.validate_token(access_token)
        return result.user

    async def logout(
        self, token: str | None = None, *, post_logout_redirect_uri: str | None = None
    ) -> str | None:
        if token is not None:
            await self._tokens.revoke_refresh_token(token)
        return post_logout_redirect_uri
