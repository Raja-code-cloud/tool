import type { ContentStatus, ContentType, PublishingStatus } from "@/lib/domain/content";

export function formatContentType(type: ContentType): string {
  const labels: Record<ContentType, string> = {
    article: "Article",
    poster: "Poster",
    video: "Video",
    thumbnail: "Thumbnail",
  };
  return labels[type];
}

export function formatContentStatus(status: ContentStatus): string {
  const labels: Record<ContentStatus, string> = {
    draft: "Draft",
    scheduled: "Scheduled",
    published: "Published",
    archived: "Archived",
  };
  return labels[status];
}

export function formatPublishingStatus(status: PublishingStatus): string {
  const labels: Record<PublishingStatus, string> = {
    not_started: "Not started",
    queued: "Queued",
    live: "Live",
    failed: "Failed",
  };
  return labels[status];
}

export function thumbnailGradient(hue: number): string {
  return `linear-gradient(135deg, hsl(${hue} 62% 42%) 0%, hsl(${(hue + 40) % 360} 55% 28%) 100%)`;
}

export function contentTypeAbbreviation(type: ContentType): string {
  const abbr: Record<ContentType, string> = {
    article: "AR",
    poster: "PO",
    video: "VI",
    thumbnail: "TH",
  };
  return abbr[type];
}
