import {
  buildGenerationPayload,
  createIdempotencyKey,
  extractPlatformContent,
  mapContentToProject,
} from "@/lib/adapters/ai-studio-mappers";
import type {
  ContentDto,
  OperationDto,
  ProviderHealthDto,
  SuccessEnvelope,
} from "@/lib/api/ai-studio-types";
import type { ApiClient } from "@/lib/api/client";
import { ApiError } from "@/lib/api/errors";
import { getWorkspaceId } from "@/lib/auth/workspace-store";
import { env } from "@/lib/config/env";
import type { AiStudioProject, AiSuggestion } from "@/lib/domain/ai-studio";
import type {
  AiStudioGenerationRequest,
  AiStudioGenerationResult,
  AiStudioProviderOption,
  AiStudioSaveDraftRequest,
  AiStudioSaveDraftResult,
} from "@/lib/domain/ai-studio-generation";
import type { AiStudioRepository } from "@/lib/domain/repositories";

const POLL_INTERVAL_MS = 2_000;
const POLL_TIMEOUT_MS = 60_000;

type ContentContext = {
  readonly contentId: string;
  readonly assetId: string;
  readonly sourceVersionId: string;
  readonly title: string;
  readonly version: number;
};

type HttpAiStudioRepositoryOptions = {
  readonly getModelId?: () => string | null;
};

function workspaceHeaders(extra?: Readonly<Record<string, string>>): Record<string, string> {
  const workspaceId = getWorkspaceId();
  if (!workspaceId) {
    throw new ApiError(
      "Workspace ID is required for AI Studio API calls. Sign in or set NEXT_PUBLIC_WORKSPACE_ID.",
      "validation_error",
      422,
    );
  }
  return {
    "X-Workspace-ID": workspaceId,
    ...extra,
  };
}

function delay(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(resolve, ms);
    if (signal) {
      if (signal.aborted) {
        clearTimeout(timer);
        reject(new ApiError("Request was cancelled", "timeout", 408));
        return;
      }
      signal.addEventListener(
        "abort",
        () => {
          clearTimeout(timer);
          reject(new ApiError("Request was cancelled", "timeout", 408));
        },
        { once: true },
      );
    }
  });
}

function resolveModelId(
  options: HttpAiStudioRepositoryOptions,
  requestModelId?: string | null,
): string {
  const modelId = requestModelId ?? options.getModelId?.() ?? env.NEXT_PUBLIC_AI_MODEL_ID;
  if (!modelId) {
    throw new ApiError(
      "AI model ID is required. Set NEXT_PUBLIC_AI_MODEL_ID or choose a provider in AI settings.",
      "validation_error",
      422,
    );
  }
  return modelId;
}

export function createHttpAiStudioRepository(
  client: ApiClient,
  options: HttpAiStudioRepositoryOptions = {},
): AiStudioRepository {
  let cachedContext: ContentContext | null = null;
  let cachedProject: AiStudioProject | null = null;
  let cachedProviders: readonly AiStudioProviderOption[] | null = null;

  async function loadContentContext(force = false): Promise<ContentContext> {
    if (cachedContext && !force) return cachedContext;

    if (env.NEXT_PUBLIC_AI_CONTENT_ID) {
      const response = await client.get<SuccessEnvelope<ContentDto>>(
        `/api/v1/content/${env.NEXT_PUBLIC_AI_CONTENT_ID}`,
        { headers: workspaceHeaders() },
      );
      const content = response.data.data;
      cachedContext = {
        contentId: content.id,
        assetId: content.assetId,
        sourceVersionId: content.contentVersionId ?? content.id,
        title: content.title,
        version: content.version,
      };
      cachedProject = mapContentToProject(content);
      return cachedContext;
    }

    const listResponse = await client.get<SuccessEnvelope<readonly ContentDto[]>>(
      "/api/v1/content?limit=1&sort=-updatedAt",
      { headers: workspaceHeaders() },
    );
    const first = listResponse.data.data[0];
    if (!first) {
      throw new ApiError(
        "No source content found for AI generation. Upload content or set NEXT_PUBLIC_AI_CONTENT_ID.",
        "not_found",
        404,
      );
    }

    cachedContext = {
      contentId: first.id,
      assetId: first.assetId,
      sourceVersionId: first.contentVersionId ?? first.id,
      title: first.title,
      version: first.version,
    };
    cachedProject = mapContentToProject(first);
    return cachedContext;
  }

  async function pollGenerationResult(
    contentId: string,
    platform: AiStudioGenerationRequest["platform"],
    baselineUpdatedAt: string,
    signal?: AbortSignal,
  ): Promise<ContentDto> {
    const deadline = Date.now() + POLL_TIMEOUT_MS;

    while (Date.now() < deadline) {
      if (signal?.aborted) {
        throw new ApiError("Generation was cancelled", "timeout", 408);
      }

      const response = await client.get<SuccessEnvelope<ContentDto>>(
        `/api/v1/content/${contentId}`,
        {
          headers: workspaceHeaders(),
          ...(signal ? { signal } : {}),
        },
      );
      const content = response.data.data;
      const platformContent = extractPlatformContent(content, platform);

      if (content.updatedAt !== baselineUpdatedAt && platformContent.content.trim().length > 0) {
        return content;
      }

      if (content.origin === "ai" || content.origin === "regeneration") {
        if (platformContent.content.trim().length > 0) {
          return content;
        }
      }

      await delay(POLL_INTERVAL_MS, signal);
    }

    throw new ApiError("Generation timed out waiting for content updates.", "timeout", 408);
  }

  async function submitGeneration(
    path: "/api/v1/content/generate" | "/api/v1/content/regenerate",
    body: Record<string, unknown>,
    signal?: AbortSignal,
  ): Promise<OperationDto> {
    const response = await client.post<SuccessEnvelope<OperationDto>>(path, body, {
      headers: workspaceHeaders({
        "Idempotency-Key": createIdempotencyKey("ai-studio"),
      }),
      ...(signal ? { signal } : {}),
    });

    if (response.status !== 202) {
      throw new ApiError("Unexpected generation response status.", "server_error", response.status);
    }

    return response.data.data;
  }

  async function runGeneration(
    request: AiStudioGenerationRequest,
    mode: "generate" | "regenerate",
  ): Promise<AiStudioGenerationResult> {
    const context = await loadContentContext();
    const modelId = resolveModelId(options, request.modelId);
    const payload = buildGenerationPayload(
      {
        assetId: context.assetId,
        sourceVersionId: context.sourceVersionId,
        modelId,
      },
      request,
    );

    const contentBefore = await client.get<SuccessEnvelope<ContentDto>>(
      `/api/v1/content/${context.contentId}`,
      {
        headers: workspaceHeaders(),
        ...(request.signal ? { signal: request.signal } : {}),
      },
    );
    const baselineUpdatedAt = contentBefore.data.data.updatedAt;

    const operation =
      mode === "regenerate"
        ? await submitGeneration(
            "/api/v1/content/regenerate",
            { ...payload, contentId: context.contentId },
            request.signal,
          )
        : await submitGeneration("/api/v1/content/generate", payload, request.signal);

    if (operation.status === "failed") {
      throw new ApiError(
        operation.errorCode ?? "Generation failed",
        operation.errorCode === "quota_exceeded" ? "quota_exceeded" : "server_error",
        500,
        operation,
        operation.errorCode ?? undefined,
      );
    }

    const contentId = operation.resourceId ?? context.contentId;
    const content = await pollGenerationResult(
      contentId,
      request.platform,
      baselineUpdatedAt,
      request.signal,
    );
    const platformContent = extractPlatformContent(content, request.platform);

    cachedContext = {
      contentId: content.id,
      assetId: content.assetId,
      sourceVersionId: content.contentVersionId ?? context.sourceVersionId,
      title: content.title,
      version: content.version,
    };
    cachedProject = mapContentToProject(content);

    return {
      ...platformContent,
      hashtags: request.generateHashtags ? platformContent.hashtags : [],
      cta: request.generateCta ? platformContent.cta : "",
      operationId: operation.id,
      contentId: content.id,
      contentVersion: content.version,
    };
  }

  return {
    async getProject(): Promise<AiStudioProject> {
      if (cachedProject) return cachedProject;
      await loadContentContext();
      return cachedProject!;
    },

    async listSuggestions(): Promise<readonly AiSuggestion[]> {
      return [];
    },

    async listProviders(): Promise<readonly AiStudioProviderOption[]> {
      if (cachedProviders) return cachedProviders;

      try {
        const response = await client.get<SuccessEnvelope<readonly ProviderHealthDto[]>>(
          "/api/v1/admin/providers?providerType=ai",
          { headers: workspaceHeaders() },
        );
        const modelId = env.NEXT_PUBLIC_AI_MODEL_ID;
        cachedProviders = response.data.data.map((provider) => ({
          id: provider.code,
          code: provider.code,
          name: provider.name,
          status: provider.status,
          modelId: modelId ?? provider.code,
        }));
        return cachedProviders;
      } catch {
        const modelId = env.NEXT_PUBLIC_AI_MODEL_ID;
        if (!modelId) return [];
        cachedProviders = [
          {
            id: modelId,
            code: "default",
            name: "Default model",
            status: "enabled",
            modelId,
          },
        ];
        return cachedProviders;
      }
    },

    generate(request: AiStudioGenerationRequest): Promise<AiStudioGenerationResult> {
      return runGeneration(request, "generate");
    },

    regenerate(request: AiStudioGenerationRequest): Promise<AiStudioGenerationResult> {
      return runGeneration(request, "regenerate");
    },

    async saveDraft(request: AiStudioSaveDraftRequest): Promise<AiStudioSaveDraftResult> {
      const context = await loadContentContext();
      const response = await client.patch<SuccessEnvelope<ContentDto>>(
        `/api/v1/content/${context.contentId}`,
        {
          title: request.title,
          bodyText: request.bodyText,
          metadata: request.metadata ?? {},
        },
        {
          headers: workspaceHeaders({
            "If-Match": String(request.contentVersion),
          }),
          ...(request.signal ? { signal: request.signal } : {}),
        },
      );

      const content = response.data.data;
      cachedContext = {
        contentId: content.id,
        assetId: content.assetId,
        sourceVersionId: content.contentVersionId ?? context.sourceVersionId,
        title: content.title,
        version: content.version,
      };
      cachedProject = mapContentToProject(content);

      return {
        savedAt: new Date().toISOString(),
        contentVersion: content.version,
      };
    },

    cancelGeneration(): void {
      // Client-side cancellation is handled via AbortSignal passed to generate().
    },
  };
}
