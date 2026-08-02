"use client";

import { Progress } from "@/components/feedback";
import { AI_STUDIO_PLATFORMS } from "@/constants/ai-studio";
import type { PlatformId } from "@/lib/domain/platform";
import {
  getPlatformLimit,
  getPlatformWarningThreshold,
  limitProgress,
  limitStatus,
} from "@/lib/utils/ai-studio";
import { cn } from "@/lib/utils/cn";
import { formatNumber } from "@/lib/utils/formatting";

export type CharacterLimitBarProps = {
  platform: PlatformId;
  current: number;
  className?: string;
};

export function CharacterLimitBar({
  platform,
  current,
  className,
}: CharacterLimitBarProps): React.JSX.Element {
  const config = AI_STUDIO_PLATFORMS.find((item) => item.id === platform);
  const limit = getPlatformLimit(platform);
  const warningAt = getPlatformWarningThreshold(platform);
  const status = limitStatus(current, limit, warningAt);
  const percent = limitProgress(current, limit);

  return (
    <div className={cn("grid gap-1.5", className)}>
      <div className="flex justify-between text-xs">
        <span>{config?.label ?? platform} limit</span>
        <span
          className={cn(
            "tabular-nums",
            status === "danger" && "text-destructive font-semibold",
            status === "warning" && "text-warning",
          )}
        >
          {formatNumber(current)} / {formatNumber(limit)}
        </span>
      </div>
      <Progress
        value={percent}
        label={`${config?.label ?? platform} character usage`}
        className={cn(
          status === "danger" && "[&_progress]:accent-destructive",
          status === "warning" && "[&_progress]:accent-warning",
        )}
      />
      {status === "danger" && (
        <p role="alert" className="text-destructive text-xs">
          Content exceeds the platform character limit.
        </p>
      )}
      {status === "warning" && (
        <p className="text-warning text-xs">Approaching the recommended character threshold.</p>
      )}
    </div>
  );
}

export type AllPlatformLimitsProps = {
  counts: Record<PlatformId, number>;
};

export function AllPlatformLimits({ counts }: AllPlatformLimitsProps): React.JSX.Element {
  return (
    <div className="grid gap-3">
      {AI_STUDIO_PLATFORMS.map((platform) => (
        <CharacterLimitBar
          key={platform.id}
          platform={platform.id}
          current={counts[platform.id] ?? 0}
        />
      ))}
    </div>
  );
}
