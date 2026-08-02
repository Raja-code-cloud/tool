/** Domain types for authentication and session management. */

export type AuthProvider = {
  readonly code: string;
  readonly name: string;
  readonly authorizationUrl: string;
  readonly pkceRequired: boolean;
};

export type AuthTokens = {
  readonly accessToken: string;
  readonly tokenType: "Bearer";
  readonly expiresIn: number;
};

export type AuthUser = {
  readonly id: string;
  readonly email: string | null;
  readonly displayName: string;
  readonly avatarUrl: string | null;
  readonly locale: string;
  readonly timeZone: string;
  readonly status: "active" | "disabled" | "anonymized";
};

export type AuthSession = {
  readonly user: AuthUser;
  readonly scopes: readonly string[];
  readonly workspaceIds: readonly string[];
  readonly access: AuthTokens | null;
};

export type AuthorizationFlow = {
  readonly authorizationUrl: string;
  readonly state: string;
  readonly codeVerifier: string;
  readonly providerCode: string;
};

export type LoginCredentials =
  | {
      readonly kind: "oauth";
      readonly providerCode: string;
      readonly authorizationCode: string;
      readonly codeVerifier: string;
      readonly redirectUri: string;
      readonly state: string;
    }
  | {
      readonly kind: "mock";
      readonly providerCode: "mock";
      readonly email: string;
      readonly redirectUri: string;
    };
