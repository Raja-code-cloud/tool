import type { PagedSuccessEnvelope, SingleSuccessEnvelope } from "@/lib/api/asset-types";
import type { SuccessEnvelope } from "@/lib/api/auth-types";

export type { PagedSuccessEnvelope, SingleSuccessEnvelope, SuccessEnvelope };

export type ScheduleStateDto =
  "draft" | "scheduled" | "paused" | "dispatched" | "completed" | "cancelled" | "failed";

export type SchedulePriorityDto = "low" | "normal" | "high";

export type AmbiguityPolicyDto = "reject" | "earlier" | "later";

export type PublicationStatusDto =
  "draft" | "ready" | "in_progress" | "completed" | "partially_failed" | "cancelled";

export type ScheduleDto = {
  readonly id: string;
  readonly version: number;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly publicationTargetId: string;
  readonly requestedLocalAt: string;
  readonly timeZone: string;
  readonly fold: 0 | 1 | null;
  readonly ambiguityPolicy: AmbiguityPolicyDto;
  readonly scheduledFor: string;
  readonly state: ScheduleStateDto;
  readonly priority: SchedulePriorityDto;
};

export type ScheduleCalendarDto = ScheduleDto & {
  readonly publicationId: string;
  readonly publicationTitle: string;
  readonly publicationStatus: PublicationStatusDto;
  readonly platformCode: string;
  readonly approvalState: string;
  readonly queueOrder: number;
};

export type CreateScheduleRequestDto = {
  readonly publicationTargetId: string;
  readonly requestedLocalAt: string;
  readonly timeZone: string;
  readonly fold?: 0 | 1;
  readonly ambiguityPolicy?: AmbiguityPolicyDto;
  readonly priority?: SchedulePriorityDto;
};

export type UpdateScheduleRequestDto = {
  readonly requestedLocalAt?: string;
  readonly timeZone?: string;
  readonly fold?: 0 | 1;
  readonly ambiguityPolicy?: AmbiguityPolicyDto;
  readonly priority?: SchedulePriorityDto;
  readonly state?: "scheduled" | "paused";
};

export type DispatchPublicationRequestDto = {
  readonly targetIds?: readonly string[];
};

export type OperationDto = {
  readonly id: string;
  readonly version: number;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly type: string;
  readonly status: "queued" | "running" | "succeeded" | "failed" | "cancelled";
  readonly resourceType: string | null;
  readonly resourceId: string | null;
  readonly errorCode: string | null;
};

export type PublicationDto = {
  readonly id: string;
  readonly version: number;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly assetId: string;
  readonly contentVersionId: string;
  readonly approvalRequestId: string | null;
  readonly title: string;
  readonly status: PublicationStatusDto;
  readonly targets: readonly {
    readonly id: string;
    readonly socialAccountId: string;
    readonly platformId: string;
    readonly approvalState: string;
    readonly externalPostId: string | null;
    readonly externalUrl: string | null;
    readonly publishedAt: string | null;
  }[];
};

export type PagedMeta = {
  readonly requestId?: string;
  readonly page?: {
    readonly nextCursor: string | null;
    readonly hasMore: boolean;
    readonly limit: number;
  };
};

export type ProblemDetail = {
  readonly success: false;
  readonly error?: {
    readonly code: string;
    readonly message: string;
    readonly details?: readonly {
      readonly field?: string;
      readonly code?: string;
      readonly message?: string;
    }[];
  };
  readonly type?: string;
  readonly title?: string;
  readonly status?: number;
  readonly detail?: string;
  readonly instance?: string;
  readonly requestId?: string;
};

export type ListSchedulesParams = {
  readonly cursor?: string;
  readonly limit?: number;
  readonly state?: readonly string[];
  readonly priority?: readonly string[];
  readonly publicationTargetId?: string;
  readonly scheduledAfter?: string;
  readonly scheduledBefore?: string;
  readonly sort?: string;
};
