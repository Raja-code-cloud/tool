import { env } from "@/lib/config/env";

let cachedWorkspaceId: string | null = null;

/** Resolve the active workspace ID for tenant-scoped API calls. */
export function resolveWorkspaceId(): string {
  const fromEnv = env.NEXT_PUBLIC_WORKSPACE_ID;
  if (fromEnv) return fromEnv;
  if (cachedWorkspaceId) return cachedWorkspaceId;
  throw new Error(
    "Workspace ID is required for AI Studio API calls. Set NEXT_PUBLIC_WORKSPACE_ID or call setActiveWorkspaceId().",
  );
}

/** Cache workspace ID from an authenticated session without modifying auth modules. */
export function setActiveWorkspaceId(workspaceId: string | null): void {
  cachedWorkspaceId = workspaceId;
}

export function getActiveWorkspaceId(): string | null {
  return env.NEXT_PUBLIC_WORKSPACE_ID ?? cachedWorkspaceId;
}
