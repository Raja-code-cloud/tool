/** Transport DTOs for AI Studio / content generation endpoints. */

import type { SuccessEnvelope } from "@/lib/api/auth-types";

export type { SuccessEnvelope };

export type GenerationScopeDto =
  | "whole"
  | "selection"
  | "headline"
  | "cta"
  | "hashtags"
  | "tone"
  | "platform_variant";

export type ContentLengthDto = "short" | "medium" | "long";

export type ContentPlatformDto =
  | "linkedin"
  | "facebook"
  | "instagram"
  | "x"
  | "medium"
  | "youtube";

export type OperationStatusDto = "queued" | "running" | "succeeded" | "failed" | "cancelled";

export type OperationDto = {
  readonly id: string;
  readonly version: number;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly type: "generation" | "publishing" | "upload" | "adminJob";
  readonly status: OperationStatusDto;
  readonly resourceType: string | null;
  readonly resourceId: string | null;
  readonly errorCode: string | null;
};

export type GenerationRequestDto = {
  readonly sourceVersionId: string;
  readonly modelId: string;
  readonly scope: GenerationScopeDto;
  readonly assetId?: string | null;
  readonly promptTemplateId?: string | null;
  readonly brandProfileId?: string | null;
  readonly parameters?: Readonly<Record<string, unknown>>;
  readonly posterAssetId?: string | null;
  readonly articleAssetId?: string | null;
  readonly videoAssetId?: string | null;
  readonly thumbnailAssetId?: string | null;
  readonly userPrompt?: string | null;
  readonly targetPlatforms?: readonly ContentPlatformDto[];
  readonly tone?: string | null;
  readonly audience?: string | null;
  readonly length?: ContentLengthDto | null;
  readonly language?: string;
  readonly hashtags?: readonly string[];
  readonly callToAction?: string | null;
  readonly selectionText?: string | null;
};

export type RegenerationRequestDto = GenerationRequestDto & {
  readonly contentId: string;
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
  readonly lifecycleStatus: "draft" | "active" | "archived";
  readonly origin: "user" | "ai" | "import" | "regeneration";
  readonly contentVersionId: string | null;
};

export type UpdateContentRequestDto = {
  readonly title: string;
  readonly bodyText?: string | null;
  readonly bodyRich?: Readonly<Record<string, unknown>> | null;
  readonly metadata?: Readonly<Record<string, unknown>>;
};

export type ProviderHealthDto = {
  readonly providerType: "ai" | "social" | "storage" | "notification" | "identity";
  readonly code: string;
  readonly name: string;
  readonly status: "enabled" | "disabled" | "degraded";
  readonly checkedAt: string;
  readonly message: string | null;
};

export type ProblemDetailsDto = {
  readonly success: false;
  readonly error?: {
    readonly code: string;
    readonly message: string;
    readonly details?: readonly {
      readonly field?: string;
      readonly code: string;
      readonly message: string;
    }[];
  };
  readonly status?: number;
  readonly detail?: string;
};
