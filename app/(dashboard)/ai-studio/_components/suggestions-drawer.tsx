"use client";

import { SecondaryButton } from "@/components/buttons";
import { Dialog, DrawerContent } from "@/components/dialogs";
import { Alert } from "@/components/feedback";
import { Badge } from "@/components/ui";
import type { AiSuggestion } from "@/lib/domain/ai-studio";

export type SuggestionsDrawerProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  suggestions: readonly AiSuggestion[];
};

const CATEGORY_LABELS = {
  grammar: "Grammar",
  seo: "SEO",
  engagement: "Engagement",
  readability: "Readability",
  timing: "Best posting time",
  warning: "Platform warnings",
} as const;

const CATEGORY_VARIANT = {
  grammar: "info",
  seo: "success",
  engagement: "info",
  readability: "neutral",
  timing: "warning",
  warning: "danger",
} as const;

export function SuggestionsDrawer({
  open,
  onOpenChange,
  suggestions,
}: SuggestionsDrawerProps): React.JSX.Element {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DrawerContent
        side="right"
        title="AI suggestions"
        description="Improvements for grammar, SEO, engagement, and platform fit."
        className="max-w-md"
      >
        {suggestions.length === 0 ? (
          <p className="text-muted-foreground text-sm">
            No suggestions yet. Generate content to receive AI-powered recommendations.
          </p>
        ) : (
          <ul className="grid gap-3">
            {suggestions.map((suggestion) => (
              <li key={suggestion.id}>
                <Alert
                  variant={
                    CATEGORY_VARIANT[suggestion.category] === "danger"
                      ? "destructive"
                      : CATEGORY_VARIANT[suggestion.category]
                  }
                  title={suggestion.title}
                  description={suggestion.description}
                  action={
                    suggestion.action ? (
                      <SecondaryButton type="button" size="compact">
                        {suggestion.action}
                      </SecondaryButton>
                    ) : undefined
                  }
                />
                <Badge variant="neutral" className="mt-2">
                  {CATEGORY_LABELS[suggestion.category]}
                </Badge>
              </li>
            ))}
          </ul>
        )}
      </DrawerContent>
    </Dialog>
  );
}
