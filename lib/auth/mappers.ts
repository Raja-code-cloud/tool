import type { AuthProviderDto, SessionDto, UserDto } from "@/lib/api/auth-types";
import { hasPermission } from "@/lib/auth/permissions";
import type { AuthProvider, AuthSession, AuthTokens, AuthUser } from "@/lib/domain/auth";
import type { WorkspaceUser } from "@/lib/domain/workspace";

function mapUser(dto: UserDto): AuthUser {
  return {
    id: dto.id,
    email: dto.email,
    displayName: dto.displayName,
    avatarUrl: dto.avatarUrl ?? null,
    locale: dto.locale,
    timeZone: dto.timeZone,
    status: dto.status,
  };
}

function mapTokens(dto: NonNullable<SessionDto["access"]>): AuthTokens {
  return {
    accessToken: dto.accessToken,
    tokenType: "Bearer",
    expiresIn: dto.expiresIn,
  };
}

export function mapSessionDto(dto: SessionDto): AuthSession {
  return {
    user: mapUser(dto.user),
    scopes: dto.scopes,
    workspaceIds: dto.workspaceIds,
    access: dto.access ? mapTokens(dto.access) : null,
  };
}

export function mapAuthProviderDto(dto: AuthProviderDto): AuthProvider {
  return {
    code: dto.code,
    name: dto.name,
    authorizationUrl: dto.authorizationUrl,
    pkceRequired: dto.pkceRequired,
  };
}

export function sessionToWorkspaceUser(session: AuthSession): WorkspaceUser {
  const permissions = session.scopes;
  let role = "Member";
  if (hasPermission(permissions, "*") || hasPermission(permissions, "admin:read")) {
    role = "Administrator";
  } else if (hasPermission(permissions, "content:write")) {
    role = "Editor";
  }
  return {
    name: session.user.displayName,
    email: session.user.email ?? "",
    role,
  };
}
