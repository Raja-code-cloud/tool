import { PLATFORM_VISUALS } from "@/lib/config/platforms";
import type { PlatformId } from "@/lib/domain/platform";
import type { FuturePlatformId, SocialAccountFilter } from "@/lib/domain/social-account";

export const SUPPORTED_PLATFORMS: readonly { id: PlatformId; label: string }[] =
  PLATFORM_VISUALS.map(({ id, label }) => ({ id, label }));
export const COMING_SOON_PLATFORMS: readonly { id: FuturePlatformId; label: string }[] = [
  { id: "threads", label: "Threads" },
  { id: "hashnode", label: "Hashnode" },
  { id: "devto", label: "Dev.to" },
  { id: "tiktok", label: "TikTok" },
  { id: "newsletter", label: "Newsletter" },
];
export const SOCIAL_ACCOUNT_FILTERS: readonly { value: SocialAccountFilter; label: string }[] = [
  { value: "all", label: "All accounts" },
  { value: "connected", label: "Connected" },
  { value: "disconnected", label: "Disconnected" },
  { value: "healthy", label: "Healthy" },
  { value: "error", label: "Error" },
  ...SUPPORTED_PLATFORMS.map(({ id, label }) => ({ value: id, label })),
];
