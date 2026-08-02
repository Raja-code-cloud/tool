"""OAuth flow utilities with PKCE, state, and nonce support."""

from __future__ import annotations

from dataclasses import dataclass

from authlib.integrations.httpx_client import AsyncOAuth2Client

from .models import AuthorizationRequest
from .utils import generate_code_challenge, generate_code_verifier, generate_nonce, generate_state


@dataclass(frozen=True, slots=True)
class OAuthSession:
    state: str
    nonce: str
    code_verifier: str
    code_challenge: str
    redirect_uri: str


class OAuthFlowManager:
    def begin(self, redirect_uri: str) -> OAuthSession:
        code_verifier = generate_code_verifier()
        return OAuthSession(
            state=generate_state(),
            nonce=generate_nonce(),
            code_verifier=code_verifier,
            code_challenge=generate_code_challenge(code_verifier),
            redirect_uri=redirect_uri,
        )

    def to_authorization_request(
        self, session: OAuthSession, *, authorization_url: str, provider: str
    ) -> AuthorizationRequest:
        return AuthorizationRequest(
            url=authorization_url,
            state=session.state,
            nonce=session.nonce,
            code_verifier=session.code_verifier,
            code_challenge=session.code_challenge,
            provider=provider,
        )


def build_oauth_client(
    *,
    client_id: str,
    client_secret: str | None,
    redirect_uri: str,
    scope: tuple[str, ...],
    token_endpoint: str,
) -> AsyncOAuth2Client:
    return AsyncOAuth2Client(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=" ".join(scope),
        token_endpoint=token_endpoint,
    )
