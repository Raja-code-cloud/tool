import type { PlatformConfig } from "@/lib/domain/ai-studio";
import type { PlatformId } from "@/lib/domain/platform";

export const AI_STUDIO_PLATFORMS: readonly PlatformConfig[] = [
  {
    id: "linkedin",
    label: "LinkedIn",
    characterLimit: 3000,
    warningThreshold: 2550,
    tip: "Lead with a insight hook. Use line breaks every 2–3 sentences for scanability.",
  },
  {
    id: "facebook",
    label: "Facebook",
    characterLimit: 63206,
    warningThreshold: 500,
    tip: "Keep posts under 500 characters for highest engagement on Facebook.",
  },
  {
    id: "instagram",
    label: "Instagram",
    characterLimit: 2200,
    warningThreshold: 1870,
    tip: "Front-load the hook before the “more” fold. Place hashtags after a line break.",
  },
  {
    id: "x",
    label: "X (Twitter)",
    characterLimit: 280,
    warningThreshold: 238,
    tip: "One idea per tweet. Thread mode works well for step-by-step technical guides.",
  },
  {
    id: "medium",
    label: "Medium",
    characterLimit: 100000,
    warningThreshold: 85000,
    tip: "Use a compelling subtitle and clear section headers for long-form readers.",
  },
  {
    id: "youtube",
    label: "YouTube",
    characterLimit: 5000,
    warningThreshold: 4250,
    tip: "Put keywords in the first 150 characters. Include timestamps for longer videos.",
  },
];

export const PLATFORM_TIPS: Record<PlatformId, readonly string[]> = {
  linkedin: [
    "Use line breaks every 2–3 sentences.",
    "Tag no more than 5 relevant companies or people.",
    "Native documents outperform link posts for reach.",
  ],
  facebook: [
    "Keep copy under 500 characters for feed engagement.",
    "Ask a direct question to prompt comments.",
    "Use a single strong visual with minimal text overlay.",
  ],
  instagram: [
    "Hook in the first 125 characters.",
    "Use 5–10 targeted hashtags, not 30 generic ones.",
    "Add alt text to carousel slides for accessibility.",
  ],
  x: [
    "One clear idea per tweet in threads.",
    "Place links in the final tweet for better reach.",
    "Use thread numbering (1/N) for long guides.",
  ],
  medium: [
    "Subtitle should promise a specific outcome.",
    "Use H2 headers every 300–400 words.",
    "Include a code snippet or diagram reference.",
  ],
  youtube: [
    "Front-load keywords in the first 150 characters.",
    "Add chapter timestamps for videos over 3 minutes.",
    "Include 3–5 hashtags above the fold.",
  ],
};

export const AI_STUDIO_TONES = [
  { value: "professional" as const, label: "Professional" },
  { value: "friendly" as const, label: "Friendly" },
  { value: "technical" as const, label: "Technical" },
  { value: "executive" as const, label: "Executive" },
  { value: "educational" as const, label: "Educational" },
];

export const AI_STUDIO_LENGTHS = [
  { value: "short" as const, label: "Short" },
  { value: "medium" as const, label: "Medium" },
  { value: "long" as const, label: "Long" },
];

export const AI_STUDIO_AUDIENCES = [
  { value: "developers" as const, label: "Developers" },
  { value: "architects" as const, label: "Architects" },
  { value: "managers" as const, label: "Managers" },
  { value: "students" as const, label: "Students" },
  { value: "decision-makers" as const, label: "Decision makers" },
];

export const AI_STUDIO_DRAFT_STORAGE_KEY = "cch:ai-studio-draft";
