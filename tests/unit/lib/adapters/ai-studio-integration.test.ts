import { describe, expect, it } from "vitest";

import { mapAiStudioError, mapStatusToApiError } from "@/lib/adapters/ai-studio-errors";
import { buildGenerationPayload, extractPlatformContent } from "@/lib/adapters/ai-studio-mappers";
import type { ContentDto } from "@/lib/api/ai-studio-types";

describe("ai studio mappers", () => {
  it("extracts platform-specific metadata from content", () => {
    const content: ContentDto = {
      id: "content-1",
      version: 2,
      createdAt: "2026-01-01T00:00:00.000Z",
      updatedAt: "2026-01-02T00:00:00.000Z",
      assetId: "asset-1",
      title: "Azure landing zones",
      bodyText: "Fallback body",
      bodyRich: null,
      metadata: {
        platforms: {
          linkedin: {
            text: "LinkedIn copy",
            hashtags: ["#azure"],
            cta: "Read more",
          },
        },
      },
      lifecycleStatus: "draft",
      origin: "ai",
      contentVersionId: "version-1",
    };

    expect(extractPlatformContent(content, "linkedin")).toEqual({
      content: "LinkedIn copy",
      hashtags: ["#azure"],
      cta: "Read more",
    });
  });

  it("builds generation payloads with tone and platform scope", () => {
    const payload = buildGenerationPayload(
      {
        assetId: "asset-1",
        sourceVersionId: "version-1",
        modelId: "model-1",
      },
      {
        platform: "linkedin",
        tone: "technical",
        length: "short",
        audience: "developers",
        generateHashtags: true,
        generateCta: false,
      },
    );

    expect(payload.scope).toBe("platform_variant");
    expect(payload.targetPlatforms).toEqual(["linkedin"]);
    expect(payload.tone).toBe("technical");
  });
});

describe("ai studio error mapping", () => {
  it("maps backend validation failures", () => {
    const error = mapStatusToApiError(422, {
      error: { code: "validation_failed", message: "userPrompt is too long" },
    });
    expect(error.code).toBe("validation_error");
    expect(error.backendCode).toBe("validation_failed");
  });

  it("maps quota and provider failures to user-facing messages", () => {
    const quota = mapAiStudioError(
      mapStatusToApiError(429, { error: { code: "quota_exceeded", message: "Quota exceeded" } }),
    );
    expect(quota.title).toBe("Quota exceeded");

    const unavailable = mapAiStudioError(
      mapStatusToApiError(503, {
        error: { code: "provider_unavailable", message: "Provider unavailable" },
      }),
    );
    expect(unavailable.title).toBe("Provider unavailable");
  });
});
