import type { AiAudience, AiLength, AiTone, ApprovalStatus } from "@/lib/domain/ai-studio";
import type { PlatformId } from "@/lib/domain/platform";

export type LoadingPhase = "idle" | "thinking" | "generating" | "regenerating" | "saving";

export type ContentVersion = {
  readonly id: string;
  readonly label: string;
  readonly content: string;
  readonly hashtags: readonly string[];
  readonly cta: string;
  readonly createdAt: string;
  readonly source: "ai" | "user" | "transform";
};

export type PlatformWorkspaceState = {
  content: string;
  hashtags: readonly string[];
  cta: string;
  versions: ContentVersion[];
  activeVersionIndex: number;
  approvalStatus: ApprovalStatus;
  undoStack: readonly string[];
  redoStack: readonly string[];
  isGenerated: boolean;
};

export type AiStudioSettings = {
  tone: AiTone;
  length: AiLength;
  audience: AiAudience;
  modelId: string | null;
  generateHashtags: boolean;
  generateCta: boolean;
  generateSeo: boolean;
  emojiOptimization: boolean;
  threadMode: boolean;
};

export type MobilePanel = "assets" | "workspace" | "preview";

export const DEFAULT_AI_SETTINGS: AiStudioSettings = {
  tone: "professional",
  length: "medium",
  audience: "architects",
  modelId: null,
  generateHashtags: true,
  generateCta: true,
  generateSeo: true,
  emojiOptimization: false,
  threadMode: true,
};

export function createEmptyPlatformState(): PlatformWorkspaceState {
  return {
    content: "",
    hashtags: [],
    cta: "",
    versions: [],
    activeVersionIndex: -1,
    approvalStatus: "draft",
    undoStack: [],
    redoStack: [],
    isGenerated: false,
  };
}

export function createInitialPlatformStates(): Record<PlatformId, PlatformWorkspaceState> {
  return {
    linkedin: createEmptyPlatformState(),
    facebook: createEmptyPlatformState(),
    instagram: createEmptyPlatformState(),
    x: createEmptyPlatformState(),
    medium: createEmptyPlatformState(),
    youtube: createEmptyPlatformState(),
  };
}
