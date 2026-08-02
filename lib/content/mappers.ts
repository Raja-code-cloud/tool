import type { AssetDto, AssetLifecycleStatusDto, ContentDto } from "@/lib/api/asset-types";
import type {
  ContentItem,
  ContentStatus,
  ContentType,
  PublishingStatus,
} from "@/lib/domain/content";

function hashToHue(id: string): number {
  let hash = 0;
  for (let index = 0; index < id.length; index += 1) {
    hash = (hash * 31 + id.charCodeAt(index)) % 360;
  }
  return hash;
}

function mapAssetType(type: string): ContentType {
  if (type === "article" || type === "poster" || type === "video" || type === "thumbnail") {
    return type;
  }
  return "article";
}

function mapLifecycleToStatus(lifecycle: AssetLifecycleStatusDto): ContentStatus {
  switch (lifecycle) {
    case "draft":
      return "draft";
    case "active":
      return "published";
    case "archived":
      return "archived";
    default: {
      const _exhaustive: never = lifecycle;
      return _exhaustive;
    }
  }
}

export function mapStatusToLifecycle(status: ContentStatus): AssetLifecycleStatusDto | null {
  switch (status) {
    case "draft":
      return "draft";
    case "published":
      return "active";
    case "archived":
      return "archived";
    case "scheduled":
      return null;
    default: {
      const _exhaustive: never = status;
      return _exhaustive;
    }
  }
}

function derivePublishingStatus(media: AssetDto["media"]): PublishingStatus {
  if (!media) return "not_started";
  switch (media.scanStatus) {
    case "pending":
      return "queued";
    case "clean":
      return "live";
    case "infected":
    case "failed":
      return "failed";
    default:
      return "not_started";
  }
}

function extractPlatforms(
  metadata: Readonly<Record<string, unknown>> | undefined,
): readonly string[] {
  if (!metadata) return [];
  const platforms = metadata.platforms;
  if (Array.isArray(platforms)) {
    return platforms.filter((value): value is string => typeof value === "string");
  }
  return [];
}

export function mapAssetDtoToContentItem(asset: AssetDto): ContentItem {
  const metadataPlatforms = extractPlatforms(
    asset.media?.extractedMetadata as Readonly<Record<string, unknown>> | undefined,
  );

  return {
    id: asset.id,
    version: asset.version,
    title: asset.title,
    type: mapAssetType(asset.assetType),
    status: mapLifecycleToStatus(asset.lifecycleStatus),
    publishingStatus: derivePublishingStatus(asset.media),
    platforms: metadataPlatforms,
    tags: [...asset.tagIds],
    author: asset.ownerId ?? "You",
    summary: asset.summary ?? "",
    createdAt: asset.createdAt,
    updatedAt: asset.updatedAt,
    isFavorite: asset.isFavorite,
    thumbnailHue: hashToHue(asset.id),
    downloadUrl: asset.media?.downloadUrl ?? null,
  };
}

export function mapContentDtoToContentItem(content: ContentDto): ContentItem {
  const metadataPlatforms = extractPlatforms(content.metadata);

  return {
    id: content.id,
    version: content.version,
    title: content.title,
    type: "article",
    status: mapLifecycleToStatus(content.lifecycleStatus),
    publishingStatus: "not_started",
    platforms: metadataPlatforms,
    tags: [],
    author: "You",
    summary: content.bodyText?.slice(0, 200) ?? "",
    createdAt: content.createdAt,
    updatedAt: content.updatedAt,
    isFavorite: false,
    thumbnailHue: hashToHue(content.assetId),
    downloadUrl: null,
    assetId: content.assetId,
  };
}
