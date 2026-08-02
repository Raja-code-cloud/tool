import type { PlatformId, PlatformVisual } from "@/lib/domain/platform";

export const PLATFORM_VISUALS = [
  {
    id: "linkedin",
    label: "LinkedIn",
    color: "#0A66C2",
    bgClass: "bg-[#0A66C2]/15",
    borderClass: "border-[#0A66C2]/50",
    textClass: "text-[#0A66C2]",
  },
  {
    id: "facebook",
    label: "Facebook",
    color: "#1877F2",
    bgClass: "bg-[#1877F2]/15",
    borderClass: "border-[#1877F2]/50",
    textClass: "text-[#1877F2]",
  },
  {
    id: "instagram",
    label: "Instagram",
    color: "#E4405F",
    bgClass: "bg-[#E4405F]/15",
    borderClass: "border-[#E4405F]/50",
    textClass: "text-[#E4405F]",
  },
  {
    id: "x",
    label: "X (Twitter)",
    color: "#1DA1F2",
    bgClass: "bg-[#1DA1F2]/15",
    borderClass: "border-[#1DA1F2]/50",
    textClass: "text-[#1DA1F2]",
  },
  {
    id: "medium",
    label: "Medium",
    color: "#00AB6C",
    bgClass: "bg-[#00AB6C]/15",
    borderClass: "border-[#00AB6C]/50",
    textClass: "text-[#00AB6C]",
  },
  {
    id: "youtube",
    label: "YouTube",
    color: "#FF0000",
    bgClass: "bg-[#FF0000]/15",
    borderClass: "border-[#FF0000]/50",
    textClass: "text-[#FF0000]",
  },
] satisfies readonly PlatformVisual[];

export const SUPPORTED_PLATFORM_IDS = new Set<PlatformId>(PLATFORM_VISUALS.map(({ id }) => id));

export function getPlatformVisual(id: PlatformId): PlatformVisual {
  const visual = PLATFORM_VISUALS.find((platform) => platform.id === id);
  if (!visual) throw new Error(`Missing platform configuration for ${id}`);
  return visual;
}

export function isPlatformId(id: string): id is PlatformId {
  return SUPPORTED_PLATFORM_IDS.has(id as PlatformId);
}
