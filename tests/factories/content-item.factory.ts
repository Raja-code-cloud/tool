import type { ContentItem } from "@/lib/domain/content";

import { createFactory } from "./create-factory";

export const contentItemFactory = createFactory<ContentItem>((sequence) => ({
  id: `content-${sequence}`,
  title: `Test Content ${sequence}`,
  type: "article",
  status: "draft",
  publishingStatus: "not_started",
  platforms: ["LinkedIn"],
  tags: ["testing"],
  author: "QA Engineer",
  summary: `Summary for test content ${sequence}.`,
  createdAt: "2026-07-01T09:00:00.000Z",
  updatedAt: "2026-08-01T12:00:00.000Z",
  isFavorite: false,
  thumbnailHue: 210,
}));
