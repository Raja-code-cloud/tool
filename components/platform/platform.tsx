import { Facebook, Instagram, Linkedin, Youtube } from "lucide-react";
import type { ComponentType, HTMLAttributes } from "react";

import { Avatar, Badge, type BadgeProps } from "@/components/ui";
import { PLATFORM_VISUALS } from "@/lib/config/platforms";
import type { PlatformId, PlatformVisual } from "@/lib/domain/platform";
import { cn } from "@/lib/utils/cn";

export type PlatformConfig = PlatformVisual & {
  readonly icon?: ComponentType<{ className?: string; "aria-hidden"?: boolean }>;
  readonly fallback: string;
};

const PLATFORM_PRESENTATION = {
  linkedin: { icon: Linkedin, fallback: "in" },
  facebook: { icon: Facebook, fallback: "f" },
  instagram: { icon: Instagram, fallback: "ig" },
  x: { fallback: "x" },
  medium: { fallback: "m" },
  youtube: { icon: Youtube, fallback: "yt" },
} satisfies Record<PlatformId, Pick<PlatformConfig, "fallback" | "icon">>;

export const PLATFORM_CONFIG: readonly PlatformConfig[] = PLATFORM_VISUALS.map((visual) => ({
  ...visual,
  ...PLATFORM_PRESENTATION[visual.id],
}));

export const SUPPORTED_PLATFORM_IDS = new Set<PlatformId>(PLATFORM_CONFIG.map(({ id }) => id));

export function getPlatformConfig(id: PlatformId): PlatformConfig {
  const config = PLATFORM_CONFIG.find((platform) => platform.id === id);
  if (!config) throw new Error(`Missing platform configuration for ${id}`);
  return config;
}

export function isPlatformId(id: string): id is PlatformId {
  return SUPPORTED_PLATFORM_IDS.has(id as PlatformId);
}

export type PlatformIconProps = HTMLAttributes<HTMLSpanElement> & {
  platform: PlatformId;
  label?: string;
};
export function PlatformIcon({
  platform,
  label,
  className,
  ...props
}: PlatformIconProps): React.JSX.Element {
  const config = getPlatformConfig(platform);
  const Icon = config.icon;
  return (
    <span
      role={label ? "img" : undefined}
      aria-label={label}
      aria-hidden={label ? undefined : true}
      className={cn(
        "inline-grid size-5 place-items-center text-xs font-bold",
        config.textClass,
        className,
      )}
      {...props}
    >
      {Icon ? <Icon className="size-full" aria-hidden={true} /> : config.fallback.toUpperCase()}
    </span>
  );
}

export type PlatformChipProps = HTMLAttributes<HTMLSpanElement> & {
  platform: PlatformId;
  showIcon?: boolean;
};
export function PlatformChip({
  platform,
  showIcon = false,
  className,
  ...props
}: PlatformChipProps): React.JSX.Element {
  const config = getPlatformConfig(platform);
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-xs font-semibold",
        config.bgClass,
        config.textClass,
        config.borderClass,
        className,
      )}
      {...props}
    >
      {showIcon && <PlatformIcon platform={platform} className="size-3" />}
      {config.label}
    </span>
  );
}

export type PlatformBadgeProps = Omit<BadgeProps, "children"> & {
  platform: PlatformId;
  showIcon?: boolean;
};
export function PlatformBadge({
  platform,
  showIcon = true,
  className,
  ...props
}: PlatformBadgeProps): React.JSX.Element {
  const config = getPlatformConfig(platform);
  return (
    <Badge
      className={cn(config.bgClass, config.textClass, config.borderClass, "border", className)}
      {...props}
    >
      {showIcon && <PlatformIcon platform={platform} className="size-3" />}
      {config.label}
    </Badge>
  );
}

export type PlatformAvatarProps = Omit<React.ComponentProps<typeof Avatar>, "alt" | "fallback"> & {
  platform: PlatformId;
};
export function PlatformAvatar({
  platform,
  className,
  ...props
}: PlatformAvatarProps): React.JSX.Element {
  const config = getPlatformConfig(platform);
  return (
    <Avatar
      alt={config.label}
      fallback={config.fallback.toUpperCase()}
      className={cn(config.bgClass, config.textClass, className)}
      {...props}
    />
  );
}

export type PlatformDotsProps = HTMLAttributes<HTMLSpanElement> & {
  platforms: readonly PlatformId[];
  size?: "sm" | "md";
};
export function PlatformDots({
  platforms,
  size = "sm",
  className,
  ...props
}: PlatformDotsProps): React.JSX.Element {
  return (
    <span
      className={cn("inline-flex gap-1", className)}
      aria-label={platforms.map((platform) => getPlatformConfig(platform).label).join(", ")}
      {...props}
    >
      {platforms.map((platform) => {
        const config = getPlatformConfig(platform);
        return (
          <span
            key={platform}
            className={cn("rounded-full", size === "sm" ? "size-2.5" : "size-3", config.bgClass)}
            style={{ boxShadow: `inset 0 0 0 1px ${config.color}` }}
            title={config.label}
          />
        );
      })}
    </span>
  );
}
