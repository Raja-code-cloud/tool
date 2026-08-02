import { clearAccessToken, getAccessToken, isAccessTokenExpired } from "@/lib/auth/token-store";
import type { AuthSession, LoginCredentials } from "@/lib/domain/auth";
import type { AuthRepository } from "@/lib/domain/repositories";

export function createAuthService(repository: AuthRepository) {
  let cachedSession: AuthSession | null = null;

  return {
    listProviders: () => repository.listProviders(),

    beginAuthorization: (providerCode: string, redirectUri: string) =>
      repository.beginAuthorization(providerCode, redirectUri),

    async login(credentials: LoginCredentials): Promise<AuthSession> {
      const session = await repository.login(credentials);
      cachedSession = session;
      return session;
    },

    async logout(): Promise<void> {
      try {
        await repository.logout();
      } finally {
        cachedSession = null;
        clearAccessToken();
      }
    },

    async refreshAccessToken() {
      const tokens = await repository.refreshAccessToken();
      return tokens;
    },

    async getSession(): Promise<AuthSession | null> {
      if (cachedSession && getAccessToken() && !isAccessTokenExpired()) {
        return cachedSession;
      }

      if (!getAccessToken() && isAccessTokenExpired()) {
        try {
          await repository.refreshAccessToken();
        } catch {
          cachedSession = null;
          clearAccessToken();
          return null;
        }
      }

      try {
        const session = await repository.getCurrentSession();
        cachedSession = session;
        return session;
      } catch {
        cachedSession = null;
        clearAccessToken();
        return null;
      }
    },

    getAccessToken,

    clearSession(): void {
      cachedSession = null;
      clearAccessToken();
    },
  };
}

export type AuthService = ReturnType<typeof createAuthService>;
