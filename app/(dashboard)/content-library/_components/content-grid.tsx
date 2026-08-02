"use client";

import { motion } from "framer-motion";
import { CalendarPlus, Copy, ExternalLink, Pencil, Star, Trash2 } from "lucide-react";
import Link from "next/link";

import { ContentCard } from "@/components/cards";
import { ConfirmationDialog } from "@/components/dialogs";
import { Badge, Button, Checkbox } from "@/components/ui";
import { ROUTES } from "@/constants/navigation";
import type { ContentItem } from "@/lib/domain/content";
import { MOTION_DURATION, MOTION_EASING } from "@/lib/motion";
import {
  contentTypeAbbreviation,
  formatContentType,
  thumbnailGradient,
} from "@/lib/utils/content-display";
import { formatDate } from "@/lib/utils/formatting";

import { ContentStatusBadge } from "./content-status-badge";

export type ContentGridProps = {
  items: readonly ContentItem[];
  selectedIds: ReadonlySet<string>;
  onToggleSelect: (id: string, checked: boolean) => void;
  onSelect: (item: ContentItem) => void;
  onToggleFavorite: (id: string) => void;
};

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.04 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 8 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: MOTION_DURATION.page, ease: MOTION_EASING.enter },
  },
};

export function ContentGrid({
  items,
  selectedIds,
  onToggleSelect,
  onSelect,
  onToggleFavorite,
}: ContentGridProps): React.JSX.Element {
  return (
    <motion.ul
      role="list"
      aria-label="Content grid"
      className="tablet:grid-cols-2 wide:grid-cols-3 grid gap-4"
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      {items.map((item) => {
        const isSelected = selectedIds.has(item.id);
        return (
          <motion.li key={item.id} variants={itemVariants} layout>
            <ContentCard
              as="article"
              className="group hover-raise flex h-full flex-col overflow-hidden p-0 transition-shadow duration-(--duration-medium)"
            >
              <div className="relative block w-full overflow-hidden border-b">
                <button
                  type="button"
                  className="focus-visible:ring-ring block w-full text-left focus-visible:ring-2 focus-visible:outline-none"
                  onClick={() => onSelect(item)}
                  aria-label={`Preview ${item.title}`}
                >
                  <div
                    className="flex aspect-video items-end justify-between p-3"
                    style={{ background: thumbnailGradient(item.thumbnailHue) }}
                  >
                    <span className="rounded-md bg-black/35 px-2 py-0.5 text-xs font-semibold text-white backdrop-blur-sm">
                      {contentTypeAbbreviation(item.type)}
                    </span>
                  </div>
                </button>
                <button
                  type="button"
                  className="absolute top-3 right-3 rounded-md bg-black/35 p-1.5 text-white backdrop-blur-sm transition-transform hover:scale-105 focus-visible:ring-2 focus-visible:ring-white"
                  aria-label={item.isFavorite ? "Remove from favorites" : "Add to favorites"}
                  aria-pressed={item.isFavorite}
                  onClick={() => onToggleFavorite(item.id)}
                >
                  <Star
                    className={item.isFavorite ? "size-4 fill-current" : "size-4"}
                    aria-hidden="true"
                  />
                </button>
              </div>

              <div className="flex flex-1 flex-col gap-3 p-4">
                <div className="flex items-start gap-2">
                  <Checkbox
                    checked={isSelected}
                    onCheckedChange={(checked) => onToggleSelect(item.id, checked === true)}
                    aria-label={`Select ${item.title}`}
                    onClick={(event) => event.stopPropagation()}
                  />
                  <div className="min-w-0 flex-1">
                    <h3 className="truncate text-sm font-semibold">{item.title}</h3>
                    <p className="text-small text-muted-foreground">
                      {formatContentType(item.type)} · {item.author}
                    </p>
                  </div>
                  <ContentStatusBadge status={item.status} />
                </div>

                <div className="flex flex-wrap gap-1">
                  {item.tags.slice(0, 3).map((tag) => (
                    <Badge key={tag} variant="neutral">
                      {tag}
                    </Badge>
                  ))}
                </div>

                <p className="text-small text-muted-foreground">
                  Updated {formatDate(item.updatedAt, { dateStyle: "medium" })}
                </p>

                <p className="text-small text-muted-foreground truncate">
                  {item.platforms.join(" · ")}
                </p>

                <div className="tablet:opacity-0 tablet:group-hover:opacity-100 tablet:group-focus-within:opacity-100 mt-auto flex flex-wrap gap-1 border-t pt-3 opacity-100 transition-opacity">
                  <Button
                    type="button"
                    variant="ghost"
                    size="compact"
                    onClick={() => onSelect(item)}
                  >
                    <ExternalLink className="size-3.5" aria-hidden="true" />
                    Open
                  </Button>
                  <Button type="button" variant="ghost" size="compact">
                    <Pencil className="size-3.5" aria-hidden="true" />
                    Edit
                  </Button>
                  <Button type="button" variant="ghost" size="compact">
                    <Copy className="size-3.5" aria-hidden="true" />
                    Duplicate
                  </Button>
                  <Button asChild variant="ghost" size="compact">
                    <Link href={ROUTES.scheduler}>
                      <CalendarPlus className="size-3.5" aria-hidden="true" />
                      Schedule
                    </Link>
                  </Button>
                  <ConfirmationDialog
                    trigger={
                      <Button
                        type="button"
                        variant="ghost"
                        size="compact"
                        className="text-destructive"
                      >
                        <Trash2 className="size-3.5" aria-hidden="true" />
                        Delete
                      </Button>
                    }
                    title={`Delete “${item.title}”?`}
                    description="This removes the asset from your library. Scheduled posts using it will fail."
                    confirmLabel="Delete"
                    isDestructive
                    onConfirm={() => undefined}
                  />
                </div>
              </div>
            </ContentCard>
          </motion.li>
        );
      })}
    </motion.ul>
  );
}
