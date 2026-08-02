/** Transport DTOs for asset and content API endpoints. */

import type { SuccessEnvelope } from "@/lib/api/auth-types";

export type { SuccessEnvelope };

export type PageMetaDto = {
  readonly nextCursor: string | null;
  readonly hasMore: boolean;
  readonly limit: number;
};

export type ApiMetaDto = {
  readonly requestId?: string;
  readonly page?: PageMetaDto;
};

export type PagedSuccessEnvelope<T> = {
  readonly success: true;
  readonly message: string;
  readonly data: readonly T[];
  readonly meta?: ApiMetaDto;
};

export type SingleSuccessEnvelope<T> = {
  readonly success: true;
  readonly message: string;
  readonly data: T;
  readonly meta?: ApiMetaDto;
};

export type AssetTypeDto = "article" | "video" | "poster" | "thumbnail";

export type AssetLifecycleStatusDto = "draft" | "active" | "archived";

export type ScanStatusDto = "pending" | "clean" | "infected" | "failed";

export type AssetMediaDto = {
  readonly mimeType: string;
  readonly byteSize: number;
  readonly checksumSha256: string;
  readonly scanStatus: ScanStatusDto;
  readonly filename: string | null;
  readonly extractedMetadata: Readonly<Record<string, string>>;
  readonly downloadUrl: string | null;
};

export type AssetDto = {
  readonly id: string;
  readonly version: number;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly assetType: AssetTypeDto;
  readonly title: string;
  readonly summary: string | null;
  readonly lifecycleStatus: AssetLifecycleStatusDto;
  readonly ownerId: string | null;
  readonly projectId: string | null;
  readonly folderId: string | null;
  readonly isFavorite: boolean;
  readonly tagIds: readonly string[];
  readonly media: AssetMediaDto | null;
};

export type OperationStatusDto = "queued" | "running" | "succeeded" | "failed" | "cancelled";

export type OperationDto = {
  readonly id: string;
  readonly version: number;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly type: "upload" | "generation" | "publishing" | "adminJob";
  readonly status: OperationStatusDto;
  readonly resourceType: string | null;
  readonly resourceId: string | null;
  readonly errorCode: string | null;
};

export type ContentDto = {
  readonly id: string;
  readonly version: number;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly assetId: string;
  readonly title: string;
  readonly bodyText: string | null;
  readonly bodyRich: Readonly<Record<string, unknown>> | null;
  readonly metadata: Readonly<Record<string, unknown>>;
  readonly lifecycleStatus: AssetLifecycleStatusDto;
  readonly origin: "user" | "ai" | "import" | "regeneration";
  readonly contentVersionId: string | null;
};

export type UpdateContentRequestDto = {
  readonly title: string;
  readonly bodyText?: string | null;
  readonly bodyRich?: Readonly<Record<string, unknown>> | null;
  readonly metadata?: Readonly<Record<string, unknown>>;
  readonly summary?: string | null;
  readonly lifecycleStatus?: AssetLifecycleStatusDto | null;
};

export type ProblemDetailDto = {
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
  readonly status?: number;
  readonly detail?: string;
  readonly title?: string;
};
