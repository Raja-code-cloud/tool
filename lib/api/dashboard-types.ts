import type { PagedSuccessEnvelope, SingleSuccessEnvelope } from "@/lib/api/asset-types";

export type { PagedSuccessEnvelope, SingleSuccessEnvelope };

export type NotificationDto = {
  readonly id: string;
  readonly version: number;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly typeCode: string;
  readonly title: string;
  readonly body: string;
  readonly severity: "info" | "success" | "warning" | "error";
  readonly resourceType: string | null;
  readonly resourceId: string | null;
  readonly readAt: string | null;
  readonly archivedAt: string | null;
  readonly expiresAt: string | null;
};

export type ProviderHealthDto = {
  readonly providerType: "ai" | "social" | "storage" | "notification" | "identity";
  readonly code: string;
  readonly name: string;
  readonly status: "enabled" | "disabled" | "degraded";
  readonly checkedAt: string;
  readonly message: string | null;
};

export type QueueStatusDto = {
  readonly queueName: "ai" | "media" | "notification" | "maintenance" | "publishing";
  readonly queued: number;
  readonly running: number;
  readonly retryWait: number;
  readonly failed: number;
  readonly deadLettered: number;
  readonly oldestQueuedAt: string | null;
};

export type DependencyStatusDto = {
  readonly name: string;
  readonly status: "healthy" | "degraded" | "unavailable";
};

export type SystemStatusDto = {
  readonly status: "healthy" | "degraded";
  readonly version: string;
  readonly startedAt: string;
  readonly dependencies: readonly DependencyStatusDto[];
  readonly maintenanceEnabled: boolean;
};

export type HealthDto = {
  readonly status: string;
  readonly version: string;
};

export type ProbeDto = {
  readonly status: string;
};

export type PublicationHistoryItemDto = {
  readonly id: string;
  readonly publicationId: string;
  readonly targetId: string;
  readonly stateType: string;
  readonly fromState: string | null;
  readonly toState: string;
  readonly reasonCode: string | null;
  readonly occurredAt: string;
};

export type ListSuccessEnvelope<T> = {
  readonly success: true;
  readonly message: string;
  readonly data: readonly T[];
  readonly meta?: {
    readonly requestId?: string;
    readonly warnings?: readonly string[];
  };
};
