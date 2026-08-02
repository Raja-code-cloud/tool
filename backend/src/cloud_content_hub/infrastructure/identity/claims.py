"""Map provider-specific claims into unified application identity."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime

from .models import IdentityClaims, TokenType, UnifiedIdentity, UserIdentity


def _as_frozenset(value: object) -> frozenset[str]:
    if value is None:
        return frozenset()
    if isinstance(value, str):
        return frozenset((value,))
    if isinstance(value, (list, tuple, set, frozenset)):
        return frozenset(str(item) for item in value)
    return frozenset()


def _parse_datetime(value: object) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=UTC)
    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    return None


def map_standard_claims(
    raw: Mapping[str, object],
    *,
    provider: str,
    token_type: TokenType = TokenType.ACCESS,
) -> IdentityClaims:
    audience = raw.get("aud")
    if isinstance(audience, str):
        audiences = (audience,)
    elif isinstance(audience, (list, tuple)):
        audiences = tuple(str(item) for item in audience)
    else:
        audiences = ()

    roles = _as_frozenset(raw.get("roles")) | _as_frozenset(raw.get("role"))
    groups = _as_frozenset(raw.get("groups")) | _as_frozenset(raw.get("group"))

    expires_at = _parse_datetime(raw.get("exp"))
    if expires_at is None:
        raise ValueError("exp claim is required")

    resolved_type = raw.get("token_type")
    if resolved_type in TokenType._value2member_map_:
        resolved_token_type = TokenType(str(resolved_type))
    else:
        resolved_token_type = token_type
    return IdentityClaims(
        subject=str(raw.get("sub") or raw.get("oid") or raw.get("user_id") or ""),
        issuer=str(raw.get("iss") or ""),
        audience=audiences,
        expires_at=expires_at,
        issued_at=_parse_datetime(raw.get("iat")),
        not_before=_parse_datetime(raw.get("nbf")),
        email=_optional_str(raw.get("email") or raw.get("preferred_username")),
        name=_optional_str(raw.get("name") or raw.get("display_name")),
        tenant_id=_optional_str(raw.get("tid") or raw.get("tenant_id")),
        roles=roles,
        groups=groups,
        permissions=_as_frozenset(raw.get("permissions")),
        provider=provider,
        profile_picture=_optional_str(raw.get("picture") or raw.get("avatar_url")),
        token_id=_optional_str(raw.get("jti")),
        token_type=resolved_token_type,
    )


def map_entra_claims(raw: Mapping[str, object]) -> IdentityClaims:
    claims = map_standard_claims(raw, provider="entra")
    roles = claims.roles | _as_frozenset(raw.get("wids"))
    return IdentityClaims(
        subject=claims.subject,
        issuer=claims.issuer,
        audience=claims.audience,
        expires_at=claims.expires_at,
        issued_at=claims.issued_at,
        not_before=claims.not_before,
        email=claims.email or _optional_str(raw.get("upn")),
        name=claims.name,
        tenant_id=claims.tenant_id,
        roles=roles,
        groups=claims.groups,
        permissions=claims.permissions,
        provider="entra",
        profile_picture=claims.profile_picture,
        token_id=claims.token_id,
        token_type=claims.token_type,
    )


def map_google_claims(raw: Mapping[str, object]) -> IdentityClaims:
    claims = map_standard_claims(raw, provider="google")
    return IdentityClaims(
        subject=claims.subject,
        issuer=claims.issuer,
        audience=claims.audience,
        expires_at=claims.expires_at,
        issued_at=claims.issued_at,
        not_before=claims.not_before,
        email=claims.email,
        name=claims.name or _optional_str(raw.get("given_name")),
        tenant_id=claims.tenant_id,
        roles=claims.roles,
        groups=claims.groups,
        permissions=claims.permissions,
        provider="google",
        profile_picture=claims.profile_picture,
        token_id=claims.token_id,
        token_type=claims.token_type,
    )


def map_mock_claims(raw: Mapping[str, object]) -> IdentityClaims:
    return map_standard_claims(raw, provider="mock")


def to_unified_identity(claims: IdentityClaims) -> UnifiedIdentity:
    return UnifiedIdentity(
        user_id=claims.subject,
        subject=claims.subject,
        provider=claims.provider or "unknown",
        email=claims.email,
        display_name=claims.name,
        tenant_id=claims.tenant_id,
        roles=claims.roles,
        groups=claims.groups,
        permissions=claims.permissions,
        profile_picture=claims.profile_picture,
    )


def to_user_identity(claims: IdentityClaims) -> UserIdentity:
    unified = to_unified_identity(claims)
    return UserIdentity(
        subject=unified.subject,
        provider=unified.provider,
        email=unified.email,
        display_name=unified.display_name,
        tenant_id=unified.tenant_id,
        roles=unified.roles,
        groups=unified.groups,
        permissions=unified.permissions,
        profile_picture=unified.profile_picture,
    )


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
