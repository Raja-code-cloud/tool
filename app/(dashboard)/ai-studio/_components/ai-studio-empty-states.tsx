"use client";

import { Sparkles } from "lucide-react";

import { PrimaryButton } from "@/components/buttons";
import { EmptyState } from "@/components/feedback";

export type AiStudioEmptyStateProps = {
  variant: "no-content" | "no-response" | "no-platform" | "no-preview";
  onGenerate?: () => void;
};

const COPY = {
  "no-content": {
    title: "No content yet",
    description: "Generate AI variants from your master article to get started.",
  },
  "no-response": {
    title: "No AI response",
    description: "Click Generate to create platform-optimized content for the selected tab.",
  },
  "no-platform": {
    title: "No platform selected",
    description: "Choose a platform tab to view and edit generated content.",
  },
  "no-preview": {
    title: "No preview available",
    description: "Generate content to see a live platform preview.",
  },
} as const;

export function AiStudioEmptyState({
  variant,
  onGenerate,
}: AiStudioEmptyStateProps): React.JSX.Element {
  const copy = COPY[variant];
  return (
    <EmptyState
      title={copy.title}
      description={copy.description}
      icon={<Sparkles aria-hidden="true" />}
      action={
        onGenerate ? (
          <PrimaryButton type="button" onClick={onGenerate}>
            Generate
          </PrimaryButton>
        ) : undefined
      }
      className="min-h-48 border-solid"
    />
  );
}
