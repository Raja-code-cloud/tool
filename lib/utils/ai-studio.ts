import { AI_STUDIO_PLATFORMS } from "@/lib/config/ai-studio";
import type { PlatformId } from "@/lib/domain/platform";

export function countCharacters(text: string): number {
  return text.length;
}

export function countWords(text: string): number {
  const trimmed = text.trim();
  if (!trimmed) return 0;
  return trimmed.split(/\s+/).length;
}

export function getPlatformLimit(platform: PlatformId): number {
  return AI_STUDIO_PLATFORMS.find((item) => item.id === platform)?.characterLimit ?? 3000;
}

export function getPlatformWarningThreshold(platform: PlatformId): number {
  return AI_STUDIO_PLATFORMS.find((item) => item.id === platform)?.warningThreshold ?? 2550;
}

export function limitProgress(current: number, limit: number): number {
  if (limit <= 0) return 0;
  return Math.min(100, Math.round((current / limit) * 100));
}

export function limitStatus(
  current: number,
  limit: number,
  warningAt: number,
): "ok" | "warning" | "danger" {
  if (current > limit) return "danger";
  if (current >= warningAt) return "warning";
  return "ok";
}

export function computeSeoScore(content: string, hashtags: readonly string[]): number {
  let score = 55;
  if (content.length > 100) score += 10;
  if (content.length > 400) score += 8;
  if (/azure|terraform|kubernetes|cloud/i.test(content)) score += 10;
  if (hashtags.length >= 3) score += 7;
  if (content.includes("#") || hashtags.length > 0) score += 5;
  return Math.min(98, score);
}

export function computeReadabilityScore(content: string): number {
  const words = countWords(content);
  const sentences = content.split(/[.!?]+/).filter(Boolean).length || 1;
  const avgWords = words / sentences;
  let score = 80;
  if (avgWords > 25) score -= 12;
  if (avgWords > 35) score -= 10;
  if (avgWords < 12) score += 5;
  return Math.max(52, Math.min(96, score));
}

export function computeEngagementScore(content: string, hasCta: boolean): number {
  let score = 62;
  if (content.includes("?")) score += 12;
  if (hasCta) score += 10;
  if (/\d\./.test(content) || content.includes("→") || content.includes("✅")) score += 8;
  if (countWords(content) > 40 && countWords(content) < 200) score += 6;
  return Math.min(94, score);
}

export function applyToneTransform(content: string, tone: string): string {
  switch (tone) {
    case "friendly":
      return content
        .replace(/\.$/m, "!")
        .replace("Production-ready", "Friendly guide to production-ready");
    case "technical":
      return `[Technical depth]\n\n${content}\n\nImplementation note: validate with \`terraform plan\` before merge.`;
    case "executive":
      return `Executive summary: ${content.split("\n")[0] ?? content}\n\nBusiness impact: faster time-to-market, reduced audit risk, predictable cloud spend.`;
    case "educational":
      return `Learning objective: understand Azure landing zone fundamentals.\n\n${content}`;
    default:
      return content;
  }
}

export function applyExpand(content: string): string {
  return `${content}\n\nAdditional context: Platform teams that automate subscription vending with policy inheritance typically reduce provisioning time from weeks to hours while improving compliance scores across the estate.`;
}

export function applyShorten(content: string, ratio = 0.65): string {
  const target = Math.floor(content.length * ratio);
  if (content.length <= target) return content;
  const trimmed = content.slice(0, target);
  const lastSpace = trimmed.lastIndexOf(" ");
  return `${lastSpace > 0 ? trimmed.slice(0, lastSpace) : trimmed}…`;
}

export function applyImprove(content: string): string {
  return content
    .replace(/\bvery\b/gi, "")
    .replace(/\s{2,}/g, " ")
    .replace(/—/g, "—")
    .trim();
}

export function splitThreadTweets(content: string): readonly string[] {
  return content
    .split(/\n\n+/)
    .map((part) => part.trim())
    .filter(Boolean);
}

export function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}
