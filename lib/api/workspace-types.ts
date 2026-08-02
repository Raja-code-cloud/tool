import type { SingleSuccessEnvelope } from "@/lib/api/auth-types";

export type WorkspaceDto = {
  readonly id: string;
  readonly version: number;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly organizationId: string;
  readonly name: string;
  readonly slug: string;
  readonly status: "provisioning" | "active" | "suspended" | "closing" | "closed";
  readonly timeZone: string;
  readonly retentionPolicyDays?: number | null;
};

export type WorkspaceEnvelope = SingleSuccessEnvelope<WorkspaceDto>;
