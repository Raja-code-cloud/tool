"use client";

import { AnimatePresence, motion } from "framer-motion";
import { CalendarPlus, Pencil, Send, Sparkles } from "lucide-react";
import Link from "next/link";

import { PrimaryButton, SecondaryButton } from "@/components/buttons";
import { Dialog, DrawerContent } from "@/components/dialogs";
import { Badge } from "@/components/ui";
import { ROUTES } from "@/constants/navigation";
import type { ContentItem } from "@/lib/domain/content";
import { MOTION_DURATION, MOTION_EASING } from "@/lib/motion";
import { formatContentType, thumbnailGradient } from "@/lib/utils/content-display";
import { formatDate } from "@/lib/utils/formatting";

import { ContentStatusBadge, PublishingStatusBadge } from "./content-status-badge";

export type ContentPreviewPanelProps = {
  item: ContentItem | null;
  onClose: () => void;
};

export function ContentPreviewPanel({
  item,
  onClose,
}: ContentPreviewPanelProps): React.JSX.Element {
  return (
    <Dialog
      open={item !== null}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <AnimatePresence>
        {item ? (
          <DrawerContent
            key={item.id}
            side="right"
            title={item.title}
            description={`${formatContentType(item.type)} · Last updated ${formatDate(item.updatedAt, { dateStyle: "long" })}`}
            className="max-w-lg"
          >
            <motion.div
              initial={{ opacity: 0, x: 16 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 16 }}
              transition={{ duration: MOTION_DURATION.drawer, ease: MOTION_EASING.enter }}
              className="grid gap-5"
            >
              <div
                className="aspect-video w-full rounded-lg"
                style={{ background: thumbnailGradient(item.thumbnailHue) }}
                role="img"
                aria-label={`Preview for ${item.title}`}
              />

              <section aria-labelledby="preview-summary-heading">
                <h3 id="preview-summary-heading" className="text-heading-3">
                  Article summary
                </h3>
                <p className="text-body text-muted-foreground mt-2">{item.summary}</p>
              </section>

              <section aria-labelledby="preview-platforms-heading">
                <h3 id="preview-platforms-heading" className="text-heading-3">
                  Connected platforms
                </h3>
                <ul className="mt-2 flex flex-wrap gap-2">
                  {item.platforms.map((platform) => (
                    <li key={platform}>
                      <Badge variant="info">{platform}</Badge>
                    </li>
                  ))}
                </ul>
              </section>

              <section aria-labelledby="preview-status-heading" className="flex flex-wrap gap-2">
                <h3 id="preview-status-heading" className="sr-only">
                  Publishing status
                </h3>
                <ContentStatusBadge status={item.status} />
                <PublishingStatusBadge status={item.publishingStatus} />
              </section>

              <section aria-labelledby="preview-tags-heading">
                <h3 id="preview-tags-heading" className="text-heading-3">
                  Tags
                </h3>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {item.tags.map((tag) => (
                    <Badge key={tag} variant="neutral">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </section>

              <p className="text-small text-muted-foreground">
                Created {formatDate(item.createdAt, { dateStyle: "medium" })} · Author {item.author}
              </p>

              <div className="flex flex-wrap gap-2 border-t pt-4">
                <SecondaryButton size="compact">
                  <Pencil className="size-4" aria-hidden="true" />
                  Edit
                </SecondaryButton>
                <SecondaryButton asChild size="compact">
                  <Link href={ROUTES.aiStudio}>
                    <Sparkles className="size-4" aria-hidden="true" />
                    Generate AI
                  </Link>
                </SecondaryButton>
                <SecondaryButton asChild size="compact">
                  <Link href={ROUTES.scheduler}>
                    <CalendarPlus className="size-4" aria-hidden="true" />
                    Schedule
                  </Link>
                </SecondaryButton>
                <PrimaryButton size="compact">
                  <Send className="size-4" aria-hidden="true" />
                  Publish
                </PrimaryButton>
              </div>
            </motion.div>
          </DrawerContent>
        ) : null}
      </AnimatePresence>
    </Dialog>
  );
}
