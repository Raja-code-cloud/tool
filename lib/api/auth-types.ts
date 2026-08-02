/** Transport DTOs for authentication API endpoints. */

export type SuccessEnvelope<T> = {
  readonly success: true;
  readonly message: string;
  readonly data: T;
  readonly meta?: {
    readonly requestId?: string;
  };
};

export type AuthProviderDto = {
  readonly code: string;
  readonly name: string;
  readonly authorizationUrl: string;
  readonly pkceRequired: boolean;
};

export type AuthTokensDto = {
  readonly accessToken: string;
  readonly tokenType: string;
  readonly expiresIn: number;
};

export type UserDto = {
  readonly id: string;
  readonly version: number;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly email: string | null;
  readonly displayName: string;
  readonly avatarUrl?: string | null;
  readonly locale: string;
  readonly timeZone: string;
  readonly status: "active" | "disabled" | "anonymized";
};

export type SessionDto = {
  readonly user: UserDto;
  readonly scopes: readonly string[];
  readonly workspaceIds: readonly string[];
  readonly access?: AuthTokensDto | null;
};

export type AuthorizeResponseDto = {
  readonly authorizationUrl: string;
  readonly state: string;
  readonly codeVerifier: string;
  readonly providerCode: string;
};
