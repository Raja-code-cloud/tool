import type { AuthorizeResponseDto, SessionDto, SuccessEnvelope } from "@/lib/api/auth-types";
import type { ApiClient } from "@/lib/api/client";
import { mapAuthProviderDto, mapSessionDto } from "@/lib/auth/mappers";
import { setAccessToken } from "@/lib/auth/token-store";
import { resolveWorkspaceId } from "@/lib/auth/workspace-store";
import type { AuthProvider, AuthSession, AuthTokens, LoginCredentials } from "@/lib/domain/auth";
import type { AuthRepository } from "@/lib/domain/repositories";

function unwrapSession(envelope: SuccessEnvelope<SessionDto>): AuthSession {
  const session = mapSessionDto(envelope.data);
  resolveWorkspaceId(session.workspaceIds);
  if (session.access) {
    setAccessToken(session.access.accessToken, session.access.expiresIn);
  }
  return session;
}

export function createHttpAuthRepository(client: ApiClient): AuthRepository {
  return {
    async listProviders(): Promise<readonly AuthProvider[]> {
      const response =
        await client.get<
          SuccessEnvelope<readonly import("@/lib/api/auth-types").AuthProviderDto[]>
        >("/api/v1/auth/providers");
      return response.data.data.map(mapAuthProviderDto);
    },

    async beginAuthorization(providerCode: string, redirectUri: string) {
      const response = await client.post<SuccessEnvelope<AuthorizeResponseDto>>(
        "/api/v1/auth/authorize",
        { providerCode, redirectUri },
      );
      const data = response.data.data;
      return {
        authorizationUrl: data.authorizationUrl,
        state: data.state,
        codeVerifier: data.codeVerifier,
        providerCode: data.providerCode,
      };
    },

    async login(credentials: LoginCredentials): Promise<AuthSession> {
      const body =
        credentials.kind === "oauth"
          ? {
              providerCode: credentials.providerCode,
              authorizationCode: credentials.authorizationCode,
              codeVerifier: credentials.codeVerifier,
              redirectUri: credentials.redirectUri,
              state: credentials.state,
            }
          : {
              providerCode: credentials.providerCode,
              email: credentials.email,
              redirectUri: credentials.redirectUri,
            };

      const response = await client.post<SuccessEnvelope<SessionDto>>("/api/v1/auth/login", body, {
        credentials: "include",
      });
      return unwrapSession(response.data);
    },

    async logout(): Promise<void> {
      await client.post<void>("/api/v1/auth/logout", undefined, {
        credentials: "include",
      });
    },

    async refreshAccessToken(): Promise<AuthTokens> {
      const response = await client.post<
        SuccessEnvelope<import("@/lib/api/auth-types").AuthTokensDto>
      >("/api/v1/auth/refresh", {}, { credentials: "include" });
      const tokens = {
        accessToken: response.data.data.accessToken,
        tokenType: "Bearer" as const,
        expiresIn: response.data.data.expiresIn,
      };
      setAccessToken(tokens.accessToken, tokens.expiresIn);
      return tokens;
    },

    async getCurrentSession(): Promise<AuthSession> {
      const response = await client.get<SuccessEnvelope<SessionDto>>("/api/v1/auth/me");
      const session = mapSessionDto(response.data.data);
      resolveWorkspaceId(session.workspaceIds);
      return session;
    },
  };
}
