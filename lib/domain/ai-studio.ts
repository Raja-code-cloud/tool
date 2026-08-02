import type { PlatformId } from "@/lib/domain/platform";

export type PlatformConfig = {
  readonly id: PlatformId;
  readonly label: string;
  readonly characterLimit: number;
  readonly warningThreshold: number;
  readonly tip: string;
};

export type AiTone = "professional" | "friendly" | "technical" | "executive" | "educational";
export type AiLength = "short" | "medium" | "long";
export type AiAudience = "developers" | "architects" | "managers" | "students" | "decision-makers";
export type ApprovalStatus = "draft" | "approved" | "rejected" | "changes";

export type AiStudioProject = {
  readonly id: string;
  readonly name: string;
  readonly description: string;
  readonly category: string;
  readonly tags: readonly string[];
  readonly status: "draft" | "in_review" | "approved";
  readonly wordCount: number;
  readonly readingMinutes: number;
  readonly thumbnailHue: number;
  readonly masterArticle: string;
  readonly videoDuration: string;
  readonly hasVideo: boolean;
};

export type AiSuggestion = {
  readonly id: string;
  readonly category: "grammar" | "seo" | "engagement" | "readability" | "timing" | "warning";
  readonly title: string;
  readonly description: string;
  readonly action?: string;
};
