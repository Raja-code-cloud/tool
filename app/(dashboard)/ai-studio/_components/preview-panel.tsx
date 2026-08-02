"use client";

import { motion } from "framer-motion";
import { Eye } from "lucide-react";

import { Card, CardHeader } from "@/components/cards";
import { Avatar, Badge } from "@/components/ui";
import type { AiStudioProject } from "@/lib/domain/ai-studio";
import type { PlatformId } from "@/lib/domain/platform";
import { splitThreadTweets } from "@/lib/utils/ai-studio";
import { thumbnailGradient } from "@/lib/utils/content-display";

import { AiStudioEmptyState } from "./ai-studio-empty-states";
import { AllPlatformLimits } from "./character-limit-bar";
import type { PlatformWorkspaceState } from "./types";

export type PreviewPanelProps = {
  project: AiStudioProject | null;
  platform: PlatformId;
  current: PlatformWorkspaceState;
  displayContent: string;
  platformCounts: Record<PlatformId, number>;
};

export function PreviewPanel({
  project,
  platform,
  current,
  displayContent,
  platformCounts,
}: PreviewPanelProps): React.JSX.Element {
  const hasPreview = current.isGenerated && displayContent.length > 0;

  return (
    <div className="grid gap-4">
      <Card className="overflow-hidden p-0">
        <div className="border-b p-4">
          <CardHeader
            title="Live preview"
            description="Approximate rendering — actual platforms may differ."
            headingLevel={2}
            className="mb-0"
            action={
              <Badge variant="neutral">
                <Eye className="size-3" aria-hidden="true" /> Instant
              </Badge>
            }
          />
        </div>
        <div className="p-4">
          {!hasPreview ? (
            <AiStudioEmptyState variant="no-preview" />
          ) : (
            <motion.div
              key={`${platform}-${displayContent.slice(0, 32)}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: MOTION_DURATION.page, ease: MOTION_EASING.enter }}
            >
              <PlatformPreview
                platform={platform}
                content={displayContent}
                hashtags={current.hashtags}
                cta={current.cta}
                projectName={project?.name ?? "Untitled"}
                thumbnailHue={project?.thumbnailHue ?? 210}
              />
            </motion.div>
          )}
        </div>
      </Card>

      <Card className="p-4">
        <CardHeader
          title="Character limits"
          description="Live usage across all platforms."
          className="mb-3"
        />
        <AllPlatformLimits counts={platformCounts} />
      </Card>
    </div>
  );
}

type PlatformPreviewProps = {
  platform: PlatformId;
  content: string;
  hashtags: readonly string[];
  cta: string;
  projectName: string;
  thumbnailHue: number;
};

function PlatformPreview({
  platform,
  content,
  hashtags,
  cta,
  projectName,
  thumbnailHue,
}: PlatformPreviewProps): React.JSX.Element {
  switch (platform) {
    case "linkedin":
      return (
        <article className="bg-card rounded-lg border p-4">
          <header className="flex items-center gap-3">
            <Avatar alt="Cloud Content Hub" fallback="CH" size="md" />
            <div>
              <p className="text-sm font-semibold">Cloud Content Hub</p>
              <p className="text-muted-foreground text-xs">Just now · 🌐</p>
            </div>
          </header>
          <p className="mt-3 text-sm whitespace-pre-wrap">{content}</p>
          {hashtags.length > 0 && <p className="text-info mt-2 text-sm">{hashtags.join(" ")}</p>}
          <div
            className="mt-3 aspect-video rounded-md"
            style={{ background: thumbnailGradient(thumbnailHue) }}
            role="img"
            aria-label="Post media"
          />
        </article>
      );
    case "facebook":
      return (
        <article className="bg-card rounded-lg border p-4">
          <header className="flex items-center gap-3">
            <Avatar alt="Cloud Content Hub" fallback="CH" />
            <p className="text-sm font-semibold">Cloud Content Hub</p>
          </header>
          <p className="mt-3 text-sm whitespace-pre-wrap">{content}</p>
          <div
            className="mt-3 aspect-video rounded-md"
            style={{ background: thumbnailGradient(thumbnailHue) }}
            role="img"
            aria-label="Facebook post media"
          />
          {cta && <p className="text-muted-foreground mt-2 text-xs">{cta}</p>}
        </article>
      );
    case "instagram":
      return (
        <article className="bg-card overflow-hidden rounded-lg border">
          <div
            className="aspect-square w-full"
            style={{ background: thumbnailGradient(thumbnailHue) }}
            role="img"
            aria-label="Instagram post"
          />
          <div className="p-3">
            <p className="text-sm">
              <span className="font-semibold">cloudcontenthub</span> {content.slice(0, 120)}
              {content.length > 120 ? "…" : ""}
            </p>
            {hashtags.length > 0 && (
              <p className="text-info mt-2 text-xs">{hashtags.slice(0, 8).join(" ")}</p>
            )}
          </div>
        </article>
      );
    case "x":
      return (
        <div className="grid gap-2">
          {splitThreadTweets(content).map((tweet, index) => (
            <article key={index} className="bg-card rounded-lg border p-3">
              <header className="flex items-center gap-2">
                <Avatar alt="Cloud Content Hub" fallback="CH" size="sm" />
                <p className="text-sm font-semibold">CloudContentHub</p>
                <span className="text-muted-foreground text-xs">
                  · {index + 1}/{splitThreadTweets(content).length}
                </span>
              </header>
              <p className="mt-2 text-sm whitespace-pre-wrap">{tweet}</p>
            </article>
          ))}
        </div>
      );
    case "medium":
      return (
        <article className="bg-card rounded-lg border p-4">
          <div
            className="aspect-[2/1] rounded-md"
            style={{ background: thumbnailGradient(thumbnailHue) }}
            role="img"
            aria-label="Medium header"
          />
          <h3 className="mt-4 text-xl font-bold">{projectName}</h3>
          <p className="mt-3 text-sm leading-relaxed whitespace-pre-wrap">
            {content.slice(0, 800)}
            {content.length > 800 ? "…" : ""}
          </p>
        </article>
      );
    case "youtube":
      return (
        <article className="bg-card rounded-lg border p-4">
          <div
            className="aspect-video rounded-md"
            style={{ background: thumbnailGradient(thumbnailHue) }}
            role="img"
            aria-label="YouTube thumbnail"
          />
          <h3 className="mt-3 text-base font-semibold">{projectName}</h3>
          <p className="text-muted-foreground mt-2 text-xs">
            Cloud Content Hub · 1.2K views · Just now
          </p>
          <pre className="text-muted-foreground mt-3 max-h-48 overflow-y-auto text-xs whitespace-pre-wrap">
            {content}
          </pre>
          {hashtags.length > 0 && <p className="text-info mt-2 text-xs">{hashtags.join(" ")}</p>}
        </article>
      );
    default:
      return <p className="text-muted-foreground text-sm