"use client";

import { History, Lightbulb, Save } from "lucide-react";

import { OutlineButton, PrimaryButton, SecondaryButton } from "@/components/buttons";
import { StatusBadge } from "@/components/feedback";
import { PageHeader } from "@/components/layout";
import { aiStudioService } from "@/lib/services";
import { formatDate } from "@/lib/utils/formatting";

export type AiStudioHeaderProps = {
  lastSavedAt: string | null;
  onSaveDraft: () => void;
  onOpenSuggestions: () => void;
  onToggleVersions: () => void;
  isSaving: boolean;
};

export function AiStudioHeader({
  lastSavedAt,
  onSaveDraft,
  onOpenSuggestions,
  onToggleVersions,
  isSaving,
}: AiStudioHeaderProps): React.JSX.Element {
  const project = aiStudioService.getProject();

  return (
    <PageHeader
      title="AI Studio"
      description="Transform your master article into platform-optimized content."
      actions={
        <>
          <StatusBadge variant="info">{project.status.replace("_", " ")}</StatusBadge>
          {lastSavedAt && (
            <span className="text-muted-foreground self-center text-xs">
              Saved {formatDate(lastSavedAt, { timeStyle: "medium" })}
            </span>
          )}
          <SecondaryButton type="button" onClick={onToggleVersions}>
            <History className="size-4" aria-hidden="true" /> Versions
          </SecondaryButton>
          <OutlineButton type="button" onClick={onOpenSuggestions}>
            <Lightbulb className="size-4" aria-hidden="true" /> Suggestions
          </OutlineButton>
          <SecondaryButton type="button" onClick={onSaveDraft} disabled={isSaving}>
            <Save className="size-4" aria-hidden="true" /> {isSaving ? "Saving…" : "Save draft"}
          </SecondaryButton>
          <PrimaryButton type="button">Approve all</PrimaryButton>
        </>
      }
    />
  );
}
