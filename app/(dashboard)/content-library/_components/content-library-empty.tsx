"use client";

import { Archive, CalendarPlus, Library, Tag, Trash2, X } from "lucide-react";
import Link from "next/link";

import { Toolbar } from "@/components/common";
import { NoContent, NoResults } from "@/components/feedback";
import { Button } from "@/components/ui";
import { ROUTES } from "@/constants/navigation";

export type BulkActionBarProps = {
  selectedCount: number;
  onClear: () => void;
  onArchive?: () => void;
  onDelete?: () => void;
};

export function BulkActionBar({
  selectedCount,
  onClear,
  onArchive,
  onDelete,
}: BulkActionBarProps): React.JSX.Element | null {
  if (selectedCount === 0) return null;

  return (
    <Toolbar
      label="Bulk actions"
      className="bg-card shadow-raised sticky bottom-4 z-10 rounded-xl border px-4 py-3"
      aria-live="polite"
    >
      <p className="text-sm font-semibold tabular-nums">{selectedCount} selected</p>
      <Button type="button" variant="secondary" size="compact">
        <Tag className="size-4" aria-hidden="true" />
        Tag
      </Button>
      <Button type="button" variant="secondary" size="compact">
        <CalendarPlus className="size-4" aria-hidden="true" />
        Schedule
      </Button>
      <Button type="button" variant="secondary" size="compact" onClick={onArchive}>
        <Archive className="size-4" aria-hidden="true" />
        Archive
      </Button>
      <Button type="button" variant="destructive" size="compact" onClick={onDelete}>
        <Trash2 className="size-4" aria-hidden="true" />
        Delete
      </Button>
      <Button
        type="button"
        variant="ghost"
        size="compact"
        className="ml-auto"
        onClick={onClear}
        aria-label="Clear selection"
      >
        <X className="size-4" aria-hidden="true" />
        Clear
      </Button>
    </Toolbar>
  );
}

export function ContentLibraryEmptyState({
  hasActiveFilters,
}: {
  hasActiveFilters: boolean;
}): React.JSX.Element {
  if (hasActiveFilters) {
    return (
      <NoResults
        className="min-h-80 p-10"
        title="No content matches your filters"
        description="Try adjusting your search or filter criteria."
      />
    );
  }

  return (
    <NoContent
      className="[&_h2]:text-heading-1 min-h-96 p-10"
      icon={<Library aria-hidden="true" />}
      title="Your content library is empty."
      description="Upload articles, posters, videos, and thumbnails to start building your omni-channel library."
      action={
        <Button asChild size="prominent">
          <Link href={ROUTES.upload}>Upload content</Link>
        </Button>
      }
    />
  );
}
