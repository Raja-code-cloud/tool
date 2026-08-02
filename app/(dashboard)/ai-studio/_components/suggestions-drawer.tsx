"use client";

import { SecondaryButton } from "@/components/buttons";
import { Dialog, DrawerContent } from "@/components/dialogs";
import { Alert } from "@/components/feedback";
import { Badge } from "@/components/ui";
import { aiStudioService } from "@/lib/services";

export type SuggestionsDrawerProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
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
}: SuggestionsDrawerProps): React.JSX.Element {
  const suggestions = aiStudioService.listSuggestions();
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DrawerContent
        side="right"
        title="AI suggestions"
        description="Improvements for grammar, SEO, engagement, and platform fit."
        className="max-w-md"
      >
        <ul className="grid gap-3">
          {suggestions.map((suggestion) => (
            <li key={suggestion.id}>
              <Alert
                variant={
                  CATEGORY_VARIANT[suggestion.category] === "danger"
                    ? "danger"
                    : CATEGORY_VARIANT[suggestion.category] === "warning"
                      ? "warning"
                      : CATEGORY_VARIANT[suggestion.category] === "success"
                        ? "success"
                        : "info"
                }
                title={suggestion.title}
                action={
                  suggestion.action ? (
                    <SecondaryButton type="button" size="compact">
                      {suggestion.action}
                    </SecondaryButton>
                  ) : undefined
                }
              >
                <Badge variant="neutral" className="mb-2">
                  {CATEGORY_LABELS[suggestion.category]}
                </Badge>
                {suggestion.description}
              </Alert>
            </li>
          ))}
        </ul>
      </DrawerContent>
    </Dialog>
  );
}
