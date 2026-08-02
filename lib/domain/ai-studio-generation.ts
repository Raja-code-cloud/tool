import type { AiAudience, AiLength, AiTone } from "@/lib/domain/ai-studio";
import type { PlatformId } from "@/lib/domain/platform";
import type { GeneratedPlatformContent } from "@/lib/domain/repositories";

export type GenerationScope =
  | "whole"
  | "selection"
  | "headline"
  | "cta"
  | "hashtags"
  | "tone"
  | "platform_variant";

export type AiStudioProviderOption = {
  readonly id: string;
  readonly code: string;
  readonly name: string;
  readonly status: "enabled" | "disabled" | "degraded";
  readonly modelId: string;
};

export type AiStudioGenerationRequest = {
  readonly platform: PlatformId;
  readonly tone: AiTone;
  readonly length: AiLength;
  readonly audience: AiAudience;
  readonly generateHashtags: boolean;
  readonly generateCta: boolean;
  readonly modelId?: string | null;
  readonly userPrompt?: string;
  readonly scope?: GenerationScope;
  readonly selectionText?: string;
  readonly existingContent?: string;
  readonly signal?: AbortSignal;
};

export type AiStudioGenerationResult = GeneratedPlatformContent & {
  readonly operationId: string;
  readonly contentId: string;
  readonly contentVersion: number;
};

export type AiStudioSaveDraftRequest = {
  readonly contentId: string;
  readonly contentVersion: number;
  readonly title: string;
  readonly bodyText: string;
  readonly metadata?: Readonly<Record<string, unknown>>;
  readonly signal?: AbortSignal;
};

export type AiStudioSaveDraftResult = {
  readonly savedAt: string;
  readonly contentVersion: number;
};
