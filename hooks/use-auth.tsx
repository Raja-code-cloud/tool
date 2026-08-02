"use client";

import { useRouter } from "next/navigation";
import * as React from "react";

import { ROUTES } from "@/constants/navigation";
import { CURRENT_USER } from "@/constants/workspace";
import { hasPermission } from "@/lib/auth/permissions";
import { sessionToWorkspaceUser } from "@/lib/auth/mappers";
import { setActiveWorkspaceId } from "@/lib/auth/workspace-store";
import { env } from "@/lib/config/env";
import type { AuthSession } from "@/lib/domain/auth";
import type { WorkspaceUser } from "@/lib/domain/workspace";
import { authService, isBackendAuthEnabled } from "@/lib/services";
import { clearSensitiveClientStorage } from "@/lib/security";

export type AuthContextValue = {
  readonly session: AuthSession | null;
  readonly user: WorkspaceUser | null;
  readonly isAuthenticated: boolean;
  readonly isLoading: boolean;
  readonly hasPermission: (permission: string) => boolean;
  readonly signOut: () => Promise<void>;
  readonly refreshSession: () => Promise<void>;
};

const AuthContext = React.createContext<AuthContextValue | null>(null);

export type AuthProviderProps = {
  readonly children: React.ReactNode;
};

export function AuthProvider({ children }: AuthProviderProps): React.JSX.Element {
  const router = useRouter();
  const [session, setSession] = React.useState<AuthSession | null>(null);
  const [isLoading, setIsLoading] = React.useState(isBackendAuthEnabled);

  const loadSession = React.useCallback(async () => {
    if (!isBackendAuthEnabled) {
      setActiveWorkspaceId(null);
      setSession(await authService.getSession());
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    try {
      const next = await authService.getSession();
      setSession(next);
      const workspaceId = next.workspaceIds[0] ?? env.NEXT_PUBLIC_WORKSPACE_ID ?? null;
      setActiveWorkspaceId(workspaceId);
    } catch {
      setSession(null);
      setActiveWorkspaceId(env.NEXT_PUBLIC_WORKSPACE_ID ?? null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    void loadSession();
  }, [loadSession]);

  const signOut = React.useCallback(async () => {
    await authService.logout();
    clearSensitiveClientStorage();
    setSession(null);
    router.push(ROUTES.login);
  }, [router]);

  const checkPermission = React.useCallback(
    (permission: string) => {
      if (!session) return false;
      return hasPermission(session.scopes, permission);
    },
    [session],
  );

  const user = React.useMemo(() => {
    if (session) return sessionToWorkspaceUser(session);
    if (!isBackendAuthEnabled) return CURRENT_USER;
    return null;
  }, [session]);

  const value = React.useMemo<AuthContextValue>(
    () => ({
      session,
      user,
      isAuthenticated: session !== null || !isBackendAuthEnabled,
      isLoading,
      hasPermission: checkPermission,
      signOut,
      refreshSession: loadSession,
    }),
    [session, user, isLoading, checkPermission, signOut, loadSession],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider.");
  }
  return context;
}
