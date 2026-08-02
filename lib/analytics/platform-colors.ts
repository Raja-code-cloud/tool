import type { PlatformId } from "@/lib/domain/platform";

const PLATFORM_CHART_COLORS: Record<PlatformId, string> = {
  linkedin: "var(--chart-1)",
  youtube: "var(--chart-2)",
  medium: "var(--chart-3)",
  instagram: "var(--chart-4)",
  x: "var(--chart-5)",
  facebook: "var(--chart-6)",
};

const PLATFORM_LABELS: Record<PlatformId, string> = {
  linkedin: "LinkedIn",
  facebook: "Facebook",
  instagram: "Instagram",
  x: "X (Twitter)",
  medium: "Medium",
  youtube: "YouTube",
};

const KNOWN_PLATFORMS = new Set<string>(Object.keys(PLATFORM_CHART_COLORS));

export function isKnownPlatformCode(code: string): code is PlatformId {
  return KNOWN_PLATFORMS.has(code);
}

export function platformLabel(code: PlatformId): string {
  return PLATFORM_LABELS[code];
}

export function platformChartColor(code: PlatformId): string {
  return PLATFORM_CHART_COLORS[code];
}
