"use client";

import { SecondaryButton } from "@/components/buttons";
import { Card, CardHeader } from "@/components/cards";
import { Badge } from "@/components/ui";
import { cn } from "@/lib/utils/cn";
import { formatDateTime } from "@/lib/utils/formatting";

import type { ContentVersion } from "./types";

export type VersionHistoryPanelProps = {
  versions: readonly ContentVersion[];
  activeVersionId?: string;
  compareVersionId: string | null;
  onRestore: (versionId: string) => void;
  onCompare: (versionId: string | null) => void;
  isOpen: boolean;
  onToggle: () => void;
};

export function VersionHistoryPanel({
  versions,
  activeVersionId,
  compareVersionId,
  onRestore,
  onCompare,
  isOpen,
  onToggle,
}: VersionHistoryPanelProps): React.JSX.Element | null {
  if (!isOpen && versions.length === 0) return null;

  return (
    <Card className="p-4">
      <CardHeader
        title="Version history"
        description="Compare and restore previous AI generations."
        action={
          <SecondaryButton type="button" size="compact" onClick={onToggle}>
            {isOpen ? "Hide" : "Show"}
          </SecondaryButton>
        }
        className="mb-3"
      />
      {isOpen && (
        <div className="grid gap-3">
          {versions.length === 0 ? (
            <p className="text-muted-foreground text-sm">
              No versions yet. Generate content to create version 1.
            </p>
          ) : (
            <ul className="grid gap-2">
              {versions.map((version) => (
                <li
                  key={version.id}
                  className={cn(
                    "rounded-lg border p-3",
                    version.id === activeVersionId && "border-primary bg-accent/40",
                  )}
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <p className="text-sm font-semibold">{version.label}</p>
                      <p className="text-muted-foreground text-xs">
                        {formatDateTime(version.createdAt)}
                      </p>
                    </div>
                    <Badge
                      variant={
                        version.source === "ai"
                          ? "info"
                          : version.source === "user"
                            ? "neutral"
                            : "success"
                      }
                    >
                      {version.source}
                    </Badge>
                  </div>
                  <p className="text-muted-foreground mt-2 line-clamp-2 text-xs">
                    {version.content}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <SecondaryButton
                      type="button"
                      size="compact"
                      onClick={() => onRestore(version.id)}
                    >
                      Restore
                    </SecondaryButton>
                    <SecondaryButton
                      type="button"
                      size="compact"
                      onClick={() => onCompare(compareVersionId === version.id ? null : version.id)}
                    >
                      {compareVersionId === version.id ? "Close compare" : "Compare"}
                    </SecondaryButton>
                  </div>
                </li>
              ))}
            </ul>
          )}
          {compareVersionId && versions.length > 0 && (
            <VersionCompare
              versions={versions}
              compareVersionId={compareVersionId}
              {...(activeVersionId ? { activeVersionId } : {})}
            />
          )}
        </div>
      )}
    </Card>
  );
}

function VersionCompare({
  versions,
  compareVersionId,
  activeVersionId,
}: {
  versions: readonly ContentVersion[];
  compareVersionId: string;
  activeVersionId?: string;
}): React.JSX.Element {
  const compare = versions.find((version) => version.id === compareVersionId);
  const current =
    versions.find((version) => version.id === activeVersionId) ?? versions[versions.length - 1];

  return (
    <div className="bg-muted/20 grid gap-3 rounded-lg border p-3 lg:grid-cols-2">
      <div>
        <p className="text-muted-foreground text-xs font-semibold uppercase">Current</p>
        <p className="mt-1 text-sm whitespace-pre-wrap">{current?.content ?? "—"}</p>
      </div>
      <div>
        <p className="text-muted-foreground text-xs font-semibold uppercase">
          {compare?.label ?? "Compare"}
        </p>
        <p className="mt-1 text-sm whitespace-pre-wrap">{compare?.content ?? "—"}</p>
      </div>
    </div>
  );
}
