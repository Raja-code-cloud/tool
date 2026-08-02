import { CURRENT_USER } from "@/constants/workspace";
import { setAccessToken } from "@/lib/auth/token-store";
import type {
  AuthProvider,
  AuthSession,
  AuthTokens,
  AuthorizationFlow,
  LoginCredentials,
} from "@/lib/domain/auth";
import type { AuthRepository } from "@/lib/domain/repositories";

const MOCK_ACCESS_TOKEN = "mock-access-token";
const MOCK_PROVIDERS: readonly AuthProvider[] = [
  {
    code: "mock",
    name: "Mock Provider",
    authorizationUrl: "mock://authorize",
    pkceRequired: true,
  },
];

function buildMockSession(email?: string): AuthSession {
  const resolvedEmail = email ?? CURRENT_USER.email;
  const displayName = email ? email.split("@")[0] ?? CURRENT_USER.name : CURRENT_USER.name;
  return {
    user: {
      id: "mock-user-id",
      email: resolvedEmail,
      displayName: displayName.charAt(0).toUpperCase() + displayName.slice(1),
      avatarUrl: null,
      locale: "en",
      timeZone: "UTC",
      status: "active",
    },
    scopes: ["profile:read", "assets:read", "content:read"],
    workspaceIds: [],
    access: {
      accessToken: MOCK_ACCESS_TOKEN,
      tokenType: "Bearer",
      expiresIn: 900,
    },
  };
}

/** In-memory auth for development when no backend URL is configured. */
export function createMockAuthRepository(): AuthRepository {
  let session: AuthSession | null = buildMockSession();

  return {
    async listProviders(): Promise<readonly AuthProvider[]> {
      return MOCK_PROVIDERS;
    },

    async beginAuthorization(providerCode: string, redirectUri: string): Promise<AuthorizationFlow> {
      return {
        authorizationUrl: `mock://authorize?redirect=${encodeURIComponent(redirectUri)}`,
        state: "mock-state",
        codeVerifier: "mock-verifier",
        providerCode,
      };
    },

    async login(credentials: LoginCredentials): Promise<AuthSession> {
      const email = credentials.kind === "mock" ? credentials.email : CURRENT_USER.email;
      session = buildMockSession(email);
      if (session.access) {
        setAccessToken(session.access.accessToken, session.access.expiresIn);
      }
      return session;
    },

    async logout(): Promise<void> {
      session = null;
    },

    async refreshAccessToken(): Promise<AuthTokens> {
      if (!session?.access) {
        throw new Error("No active session to refresh.");
      }
      const tokens: AuthTokens = {
        accessToken: MOCK_ACCESS_TOKEN,
        tokenType: "Bearer",
        expiresIn: 900,
      };
      setAccessToken(tokens.accessToken, tokens.expiresIn);
      return tokens;
    },

    async getCurrentSession(): Promise<AuthSession> {
      if (!session) {
        throw new Error("Not authenticated.");
      }
      return session;
    },
  };
}
