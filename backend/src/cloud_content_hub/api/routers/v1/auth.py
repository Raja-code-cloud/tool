"""Authentication HTTP routes."""

from __future__ import annotations

import secrets
import uuid
from datetime import datetime
from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from cloud_content_hub.api.responses import list_success, success
from cloud_content_hub.api.schemas.transport import (
    AuthProviderDto,
    AuthTokensDto,
    AuthorizeRequest,
    AuthorizeResponseDto,
    LoginRequest,
    RefreshRequest,
    SessionDto,
    UserDto,
    UserStatusDto,
)
from cloud_content_hub.core.errors import AuthenticationError, ClientError
from cloud_content_hub.infrastructure.identity.config import IdentitySettings
from cloud_content_hub.infrastructure.identity.dependencies import AuthenticatedPrincipal
from cloud_content_hub.infrastructure.identity.exceptions import InvalidToken, OAuthValidationError
from cloud_content_hub.infrastructure.identity.factory import IdentityFactory
from cloud_content_hub.infrastructure.identity.models import AuthenticationResult, UserIdentity
from cloud_content_hub.infrastructure.identity.principal import Principal
from cloud_content_hub.infrastructure.identity.utils import utc_now

router = APIRouter(tags=["Auth"])

_USER_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
_CSRF_COOKIE = "cch_csrf"


def _identity_factory(request: Request) -> IdentityFactory:
    return cast(IdentityFactory, request.app.state.identity_factory)


def _identity_settings(request: Request) -> IdentitySettings:
    return _identity_factory(request)._settings  # noqa: SLF001


def _subject_to_user_id(subject: str, provider: str) -> UUID:
    try:
        return UUID(subject)
    except ValueError:
        return uuid.uuid5(_USER_NAMESPACE, f"{provider}:{subject}")


def _build_user_dto(identity: UserIdentity, *, now: datetime | None = None) -> UserDto:
    timestamp = now or utc_now()
    return UserDto(
        id=_subject_to_user_id(identity.subject, identity.provider),
        version=1,
        created_at=timestamp,
        updated_at=timestamp,
        email=identity.email,
        display_name=identity.display_name or identity.subject,
        avatar_url=identity.profile_picture,
        locale="en",
        time_zone="UTC",
        status=UserStatusDto.ACTIVE,
    )


def _build_session_dto(
    result: AuthenticationResult,
    *,
    include_access: bool = True,
) -> SessionDto:
    user = _build_user_dto(result.user)
    scopes = sorted(result.user.permissions)
    access: AuthTokensDto | None = None
    if include_access and result.tokens is not None:
        access = AuthTokensDto(
            access_token=result.tokens.access_token,
            token_type=result.tokens.token_type,
            expires_in=result.tokens.expires_in or 900,
        )
    return SessionDto(user=user, scopes=scopes, workspace_ids=[], access=access)


def _session_from_principal(principal: Principal) -> SessionDto:
    identity = UserIdentity(
        subject=principal.subject,
        provider=principal.provider,
        email=principal.email,
        display_name=principal.display_name,
        tenant_id=principal.tenant_id,
        roles=principal.roles,
        groups=principal.groups,
        permissions=principal.permissions,
    )
    return SessionDto(
        user=_build_user_dto(identity),
        scopes=sorted(principal.permissions),
        workspace_ids=[],
        access=None,
    )


def _set_refresh_cookie(response: Response, token: str, settings: IdentitySettings) -> None:
    cookie = settings.cookie
    max_age = settings.refresh_token_days * 24 * 60 * 60
    response.set_cookie(
        key=cookie.name,
        value=token,
        max_age=max_age,
        path=cookie.path,
        domain=cookie.domain,
        secure=cookie.secure,
        httponly=cookie.httponly,
        samesite=cookie.samesite,  # type: ignore[arg-type]
    )


def _clear_refresh_cookie(response: Response, settings: IdentitySettings) -> None:
    cookie = settings.cookie
    response.delete_cookie(
        key=cookie.name,
        path=cookie.path,
        domain=cookie.domain,
    )


def _set_csrf_cookie(response: Response, token: str, settings: IdentitySettings) -> None:
    cookie = settings.cookie
    max_age = settings.refresh_token_days * 24 * 60 * 60
    response.set_cookie(
        key=_CSRF_COOKIE,
        value=token,
        max_age=max_age,
        path=cookie.path,
        domain=cookie.domain,
        secure=cookie.secure,
        httponly=False,
        samesite=cookie.samesite,  # type: ignore[arg-type]
    )


def _clear_csrf_cookie(response: Response, settings: IdentitySettings) -> None:
    cookie = settings.cookie
    response.delete_cookie(key=_CSRF_COOKIE, path=cookie.path, domain=cookie.domain)


def _read_refresh_token(request: Request, settings: IdentitySettings) -> str | None:
    return request.cookies.get(settings.cookie.name)


def _validate_csrf(request: Request, settings: IdentitySettings) -> None:
    cookie_token = request.cookies.get(_CSRF_COOKIE)
    header_token = request.headers.get(settings.csrf_header)
    if not cookie_token or not header_token or cookie_token != header_token:
        raise AuthenticationError(
            code="invalid_request",
            detail="CSRF token validation failed.",
        )


async def _exchange_login(
    factory: IdentityFactory,
    body: LoginRequest,
) -> AuthenticationResult:
    registry = factory.build_registry()
    provider = registry.get(body.provider_code)

    if body.authorization_code:
        if not body.redirect_uri or not body.code_verifier or not body.state:
            raise ClientError(detail="redirect_uri, code_verifier, and state are required.")
        return await provider.exchange_code(
            body.authorization_code,
            body.redirect_uri,
            state=body.state,
            expected_state=body.state,
            nonce="",
            code_verifier=body.code_verifier,
        )

    if body.provider_code == "mock" and body.email:
        redirect_uri = body.redirect_uri
        settings = factory._settings  # noqa: SLF001
        if not redirect_uri:
            if not settings.mock_redirect_uris:
                raise ClientError(detail="redirect_uri is required.")
            redirect_uri = settings.mock_redirect_uris[0]
        auth = await provider.authenticate(redirect_uri)
        subject = body.email.split("@")[0]
        code = f"mock-{subject}"
        if hasattr(provider, "issue_mock_code"):
            code = provider.issue_mock_code(subject)  # type: ignore[attr-defined]
        return await provider.exchange_code(
            code,
            redirect_uri,
            state=auth.state,
            expected_state=auth.state,
            nonce=auth.nonce,
            code_verifier=auth.code_verifier,
        )

    raise ClientError(detail="Unsupported login credentials for the selected provider.")


@router.get("/providers", operation_id="listAuthProviders")
async def list_auth_providers(request: Request) -> JSONResponse:
    factory = _identity_factory(request)
    registry = factory.build_registry()
    providers = [
        AuthProviderDto(
            code=descriptor.code,
            name=descriptor.name,
            authorization_url=descriptor.authorization_url or "",
            pkce_required=descriptor.pkce_required,
        )
        for descriptor in registry.descriptors()
        if descriptor.authorization_url
    ]
    return JSONResponse(
        list_success(items=providers, message="Authentication providers retrieved.").model_dump(
            by_alias=True
        )
    )


@router.post("/authorize", operation_id="beginAuthorization")
async def begin_authorization(
    request: Request,
    body: AuthorizeRequest,
) -> JSONResponse:
    """Start an OAuth authorization flow and return PKCE parameters for the client."""

    factory = _identity_factory(request)
    registry = factory.build_registry()
    provider = registry.get(body.provider_code)
    auth = await provider.authenticate(body.redirect_uri)
    return JSONResponse(
        success(
            data=AuthorizeResponseDto(
                authorization_url=auth.url,
                state=auth.state,
                code_verifier=auth.code_verifier,
                provider_code=auth.provider,
            ),
            message="Authorization flow started.",
        ).model_dump(by_alias=True)
    )


@router.post("/login", operation_id="login")
async def login(request: Request, body: LoginRequest) -> JSONResponse:
    factory = _identity_factory(request)
    settings = _identity_settings(request)

    try:
        result = await _exchange_login(factory, body)
    except OAuthValidationError as error:
        raise AuthenticationError(code="invalid_credentials", detail=str(error)) from error

    if result.tokens is None:
        raise AuthenticationError(detail="Authentication did not produce tokens.")

    session = _build_session_dto(result, include_access=True)
    csrf_token = secrets.token_urlsafe(32)
    response = JSONResponse(
        success(data=session, message="Signed in.").model_dump(by_alias=True)
    )
    if result.tokens.refresh_token:
        _set_refresh_cookie(response, result.tokens.refresh_token, settings)
    _set_csrf_cookie(response, csrf_token, settings)
    return response


@router.post("/logout", operation_id="logout", status_code=204)
async def logout(request: Request) -> Response:
    factory = _identity_factory(request)
    settings = _identity_settings(request)
    refresh_token = _read_refresh_token(request, settings)

    if refresh_token:
        _validate_csrf(request, settings)
        registry = factory.build_registry()
        try:
            decoded = await factory.jwt_service.decode_and_verify(refresh_token)
            provider_name = decoded.claims.provider or settings.default_provider
            provider = registry.get(provider_name)
            await provider.logout(token=refresh_token)
        except InvalidToken:
            pass

    response = Response(status_code=204)
    _clear_refresh_cookie(response, settings)
    _clear_csrf_cookie(response, settings)
    return response


@router.post("/refresh", operation_id="refreshAccessToken")
async def refresh_access_token(
    request: Request,
    body: RefreshRequest | None = None,
) -> JSONResponse:
    factory = _identity_factory(request)
    settings = _identity_settings(request)
    refresh_token = _read_refresh_token(request, settings)
    body_token = body.refresh_token if body else None

    if refresh_token and body_token:
        raise ClientError(detail="Provide refresh token via cookie or body, not both.")

    token = refresh_token or body_token
    if refresh_token:
        _validate_csrf(request, settings)

    if not token:
        raise AuthenticationError(code="refresh_token_invalid", detail="Refresh token is required.")

    try:
        token_set = await factory.token_service.refresh_access_token(token)
    except InvalidToken as error:
        raise AuthenticationError(code="refresh_token_invalid", detail=str(error)) from error

    response = JSONResponse(
        success(
            data=AuthTokensDto(
                access_token=token_set.access_token,
                token_type=token_set.token_type,
                expires_in=token_set.expires_in or settings.access_token_minutes * 60,
            ),
            message="Access token refreshed.",
        ).model_dump(by_alias=True)
    )
    if token_set.refresh_token:
        _set_refresh_cookie(response, token_set.refresh_token, settings)
    return response


@router.get("/me", operation_id="getCurrentSession")
async def get_current_session(
    principal: AuthenticatedPrincipal,
) -> JSONResponse:
    session = _session_from_principal(principal)
    return JSONResponse(
        success(data=session, message="Session retrieved.").model_dump(by_alias=True)
    )
