"use client";

import { Sparkles, X } from "lucide-react";
import Link from "next/link";
import * as React from "react";

import { IconButton } from "@/components/buttons";
import { Card, CardHeader } from "@/components/cards";
import { StatusBadge } from "@/components/feedback";
import { Button } from "@/components/ui";
import type { DashboardSuggestion } from "@/lib/domain/dashboard";
import { dashboardService } from "@/lib/services";

const PRIORITY_VARIANT = {
  high: "danger",
  medium: "warning",
  low: "info",
} as const;

function SuggestionItem({
  suggestion,
  onDismiss,
}: {
  suggestion: DashboardSuggestion;
  onDismiss: (id: string) => void;
}): React.JSX.Element {
  return (
    <li className="bg-card hover:bg-accent/30 flex gap-3 rounded-lg border p-4 transition-colors duration-(--duration-fast)">
      <Sparkles className="text-primary mt-0.5 size-4 shrink-0" aria-hidden="true" />
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <p className="text-sm font-semibold">{suggestion.title}</p>
          <StatusBadge variant={PRIORITY_VARIANT[suggestion.priority]}>
            {suggestion.priority}
          </StatusBadge>
        </div>
        <p className="text-muted-foreground mt-1 text-sm">
          <span className="text-foreground font-semibold">Why this suggestion: </span>
          {suggestion.reason}
        </p>
        <Button asChild variant="outline" size="compact" className="mt-3">
          <Link href={suggestion.href}>{suggestion.actionLabel}</Link>
        </Button>
      </div>
      <IconButton
        label={`Dismiss suggestion: ${suggestion.title}`}
        icon={<X aria-hidden="true" />}
        onClick={() => onDismiss(suggestion.id)}
        className="shrink-0"
      />
    </li>
  );
}

export function AiSuggestionsPanel(): React.JSX.Element {
  const [suggestions, setSuggestions] = React.useState<readonly DashboardSuggestion[]>(() =>
    dashboardService.listSuggestions(),
  );

  function dismiss(id: string): void {
    setSuggestions((current) => current.filter((item) => item.id !== id));
  }

  return (
    <Card as="section" aria-labelledby="ai-suggestions-heading" className="h-full">
      <CardHeader
        title="AI suggestions"
        description="Personalised next steps based on drafts, calendar gaps, and account health."
        headingLevel={2}
        headingId="ai-suggestions-heading"
      />
      {suggestions.length === 0 ? (
        <p className="text-body text-muted-foreground">
          You&apos;re caught up. No suggestions right now.
        </p>
      ) : (
        <ul className="grid gap-3">
          {suggestions.map((suggestion) => (
            <SuggestionItem key={suggestion.id} suggestion={suggestion} onDismiss={dismiss} />
          ))}
        </ul>
      )}
    </Card>
  );
}
