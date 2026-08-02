"use client";

import { FileText, Image as ImageIcon, Info, Video } from "lucide-react";

import { OutlineButton, SecondaryButton } from "@/components/buttons";
import { Card, CardHeader } from "@/components/cards";
import { KeyValueList } from "@/components/common";
import { StatusBadge } from "@/components/feedback";
import { Badge } from "@/components/ui";
import type { AiStudioProject } from "@/lib/domain/ai-studio";
import { thumbnailGradient } from "@/lib/utils/content-display";
import { formatNumber } from "@/lib/utils/formatting";

export type AssetsPanelProps = {
  project: AiStudioProject | null;
};

export function AssetsPanel({ project }: AssetsPanelProps): React.JSX.Element {
  if (!project) {
    return (
      <Card className="flex h-full flex-col overflow-hidden p-4">
        <p className="text-muted-foreground text-sm">Loading source content…</p>
      </Card>
    );
  }

  return (
    <Card className="flex h-full flex-col overflow-hidden p-0">
      <div className="border-b p-4">
        <CardHeader
          title="Content assets"
          description="Source material for AI generation."
          headingLevel={2}
          className="mb-0"
        />
      </div>
      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        <section aria-labelledby="poster-heading">
          <h3 id="poster-heading" className="mb-2 flex items-center gap-2 text-sm font-semibold">
            <ImageIcon className="size-4" aria-hidden="true" /> Poster
          </h3>
          <div
            className="aspect-video w-full rounded-lg"
            style={{ background: thumbnailGradient(project.thumbnailHue) }}
            role="img"
            aria-label={`Poster for ${project.name}`}
          />
        </section>

        <section aria-labelledby="article-heading">
          <h3 id="article-heading" className="mb-2 flex items-center gap-2 text-sm font-semibold">
            <FileText className="size-4" aria-hidden="true" /> Master article
          </h3>
          <div className="bg-muted/30 text-muted-foreground max-h-40 overflow-y-auto rounded-lg border p-3 text-xs whitespace-pre-wrap">
            {project.masterArticle.slice(0, 600)}…
          </div>
        </section>

        {project.hasVideo && (
          <section aria-labelledby="video-heading">
            <h3 id="video-heading" className="mb-2 flex items-center gap-2 text-sm font-semibold">
              <Video className="size-4" aria-hidden="true" /> Video
            </h3>
            <div className="bg-muted/40 rounded-lg border px-3 py-2 text-sm">
              Azure landing zone walkthrough · {project.videoDuration}
            </div>
          </section>
        )}

        <section aria-labelledby="thumb-heading">
          <h3 id="thumb-heading" className="mb-2 flex items-center gap-2 text-sm font-semibold">
            <ImageIcon className="size-4" aria-hidden="true" /> Thumbnail
          </h3>
          <div
            className="aspect-video w-full rounded-lg"
            style={{ background: thumbnailGradient((project.thumbnailHue + 60) % 360) }}
            role="img"
            aria-label="Video thumbnail"
          />
        </section>

        <section aria-labelledby="project-meta-heading">
          <h3
            id="project-meta-heading"
            className="mb-2 flex items-center gap-2 text-sm font-semibold"
          >
            <Info className="size-4" aria-hidden="true" /> Project information
          </h3>
          <KeyValueList
            items={[
              { id: "words", term: "Word count", description: formatNumber(project.wordCount) },
              { id: "read", term: "Reading time", description: `${project.readingMinutes} min` },
              { id: "cat", term: "Category", description: project.category },
              {
                id: "status",
                term: "Status",
                description: (
                  <StatusBadge variant="info">{project.status.replace("_", " ")}</StatusBadge>
                ),
              },
            ]}
          />
          <div className="mt-3 flex flex-wrap gap-1.5">
            {project.tags.map((tag) => (
              <Badge key={tag} variant="neutral">
                {tag}
              </Badge>
            ))}
          </div>
        </section>
      </div>
      <div className="flex flex-wrap gap-2 border-t p-4">
        <SecondaryButton type="button" size="compact">
          Replace asset
        </SecondaryButton>
        <OutlineButton type="button" size="compact">
          View details
        </OutlineButton>
      </div>
    </Card>
  );
}
