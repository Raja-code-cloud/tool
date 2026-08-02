import type { ContentDto, ContentPlatformDto } from "@/lib/api/ai-studio-types";
import type { AiStudioProject } from "@/lib/domain/ai-studio";
import type {
  AiStudioGenerationRequest,
  AiStudioGenerationResult,
} from "@/lib/domain/ai-studio-generation";
import type { PlatformId } from "@/lib/domain/platform";

export function mapPlatformIdToDto(platform: PlatformId): ContentPlatformDto {
  return platform;
}

export function mapContentToProject(content: ContentDto): AiStudioProject {
  const body = content.bodyText ?? "";
  const words = body.trim() ? body.trim().split(/\s+/).length : 0;
  const tags = Array.isArray(content.metadata.tags)
    ? (content.metadata.tags as readonly string[])
    : [];

  return {
    id: content.id,
    name: content.title,
    description: typeof content.metadata.summary === "string" ? content.metadata.summary : content.title,
    category:
      typeof content.metadata.category === "string" ? content.metadata.category : "Content",
    tags,
    status: content.lifecycleStatus === "draft" ? "draft" : "in_review",
    wordCount: words,
    readingMinutes: Math.max(1, Math.ceil(words / 200)),
    thumbnailHue:
      typeof content.metadata.thumbnailHue === "number" ? content.metadata.thumbnailHue : 210,
    masterArticle: body,
    videoDuration:
      typeof content.metadata.videoDuration === "string" ? content.metadata.videoDuration : "0:00",
    hasVideo: content.metadata.hasVideo === true,
  };
}

export function extractPlatformContent(
  content: ContentDto,
  platform: PlatformId,
): Pick<AiStudioGenerationResult, "content" | "hashtags" | "cta"> {
  const platforms = content.metadata.platforms;
  if (platforms && typeof platforms === "object") {
    const platformEntry = (platforms as Record<string, unknown>)[platform];
    if (platformEntry && typeof platformEntry === "object") {
      const entry = platformEntry as Record<string, unknown>;
      return {
        content:
          typeof entry.text === "string"
            ? entry.text
            : (content.bodyText ?? ""),
        hashtags: Array.isArray(entry.hashtags)
          ? (entry.hashtags as readonly string[])
          : [],
        cta: typeof entry.cta === "string" ? entry.cta : "",
      };
    }
  }

  return {
    content: content.bodyText ?? "",
    hashtags: Array.isArray(content.metadata.hashtags)
      ? (content.metadata.hashtags as readonly string[])
      : [],
    cta: typeof content.metadata.callToAction === "string" ? content.metadata.callToAction : "",
  };
}

export function buildGenerationPayload(
  context: {
    readonly assetId: string;
    readonly sourceVersionId: string;
    readonly modelId: string;
  },
  request: AiStudioGenerationRequest,
): Record<string, unknown> {
  const scope = request.scope ?? "platform_variant";
  return {
    assetId: context.assetId,
    sourceVersionId: context.sourceVersionId,
    modelId: request.modelId ?? context.modelId,
    scope,
    targetPlatforms: [mapPlatformIdToDto(request.platform)],
    tone: request.tone,
    audience: request.audience,
    length: request.length,
    userPrompt: request.userPrompt ?? null,
    selectionText: request.selectionText ?? null,
    language: "en",
    parameters: {},
  };
}

export function createIdempotencyKey(prefix: string): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return `${prefix}-${crypto.randomUUID()}`;
  }
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}
