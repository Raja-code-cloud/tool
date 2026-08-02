import {
  readVersionedStorage,
  removeStorageKey,
  writeVersionedStorage,
} from "@/lib/security/storage";

const WORKSPACE_ID_KEY = "cch:workspace-id";

function isWorkspaceId(value: unknown): value is string {
  return typeof value === "string" && value.length > 0;
}

let memoryWorkspaceId: string | null = null;

export function getWorkspaceId(): string | null {
  if (memoryWorkspaceId) return memoryWorkspaceId;
  const stored = readVersionedStorage(WORKSPACE_ID_KEY, isWorkspaceId);
  if (!stored.ok) return null;
  memoryWorkspaceId = stored.data;
  return stored.data;
}

export function setWorkspaceId(workspaceId: string | null): void {
  memoryWorkspaceId = workspaceId;
  if (!workspaceId) {
    removeStorageKey(WORKSPACE_ID_KEY);
    return;
  }
  writeVersionedStorage(WORKSPACE_ID_KEY, workspaceId);
}

export function resolveWorkspaceId(workspaceIds: readonly string[]): string | null {
  const current = getWorkspaceId();
  if (current && workspaceIds.includes(current)) return current;
  const next = workspaceIds[0] ?? null;
  setWorkspaceId(next);
  return next;
}
