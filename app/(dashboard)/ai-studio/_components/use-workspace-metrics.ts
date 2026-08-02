import { PLATFORM_TIPS } from "@/lib/config/ai-studio";
import type { PlatformId } from "@/lib/domain/platform";
import {
  computeEngagementScore,
  computeReadabilityScore,
  computeSeoScore,
  countCharacters,
  countWords,
} from "@/lib/utils/ai-studio";

import type { PlatformWorkspaceState } from "./types";

export function useWorkspaceMetrics(
  platform: PlatformId,
  content: string,
  current: PlatformWorkspaceState,
) {
  return {
    charCount: countCharacters(content),
    wordCount: countWords(content),
    seoScore: computeSeoScore(content, current.hashtags),
    readabilityScore: computeReadabilityScore(content),
    engagementScore: computeEngagementScore(content, Boolean(current.cta)),
    tips: PLATFORM_TIPS[platform],
  };
}
