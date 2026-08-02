import type { AssetDto, OperationDto, SingleSuccessEnvelope } from "@/lib/api/asset-types";
import type { ApiClient } from "@/lib/api/client";
import { ApiError, isApiError } from "@/lib/api/errors";
import { mapTransportError } from "@/lib/api/error-mapping";
import { getActiveWorkspaceId } from "@/lib/auth/workspace-store";
import { getAccessToken } from "@/lib/auth/token-store";
import type { ContentType } from "@/lib/domain/content";

export type UploadAssetKind = ContentType;

export type UploadAssetParams = {
  readonly assetType: UploadAssetKind;
  readonly title: string;
  readonly file: File;
  readonly summary?: string;
  readonly projectId?: string;
  readonly folderId?: string;
  readonly onProgress?: (percent: number) => void;
  readonly signal?: AbortSignal;
};

export type UploadAssetResult = {
  readonly asset: AssetDto;
  readonly operation: OperationDto;
};

export type UploadClientOptions = {
  readonly baseUrl: string;
  readonly getAccessToken?: () => string | null;
  readonly getWorkspaceId?: () => string | null;
};

function buildUrl(baseUrl: string, path: string): string {
  const normalizedBase = baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl;
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${normalizedBase}${normalizedPath}`;
}

function createIdempotencyKey(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `upload-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function buildUploadHeaders(options: UploadClientOptions): Record<string, string> {
  const headers: Record<string, string> = {
    Accept: "application/json",
    "Idempotency-Key": createIdempotencyKey(),
  };
  const token = (options.getAccessToken ?? getAccessToken)();
  if (token) headers.Authorization = `Bearer ${token}`;
  const workspaceId = (options.getWorkspaceId ?? getActiveWorkspaceId)();
  if (workspaceId) headers["X-Workspace-ID"] = workspaceId;
  return headers;
}

function parseUploadResponse(xhr: XMLHttpRequest): UploadAssetResult {
  const contentType = xhr.getResponseHeader("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    throw new ApiError("Unexpected upload response", "unknown", xhr.status);
  }
  const envelope = JSON.parse(xhr.responseText) as SingleSuccessEnvelope<OperationDto>;
  if (!envelope.success || !envelope.data.resourceId) {
    throw new ApiError("Upload accepted but resource id missing", "unknown", xhr.status, envelope);
  }
  return {
    operation: envelope.data,
    asset: {
      id: envelope.data.resourceId,
      version: envelope.data.version,
      createdAt: envelope.data.createdAt,
      updatedAt: envelope.data.updatedAt,
      assetType: "poster",
      title: "",
      summary: null,
      lifecycleStatus: "draft",
      ownerId: null,
      projectId: null,
      folderId: null,
      isFavorite: false,
      tagIds: [],
      media: null,
    },
  };
}

/** XMLHttpRequest upload with progress events for multipart asset uploads. */
export function uploadAssetMultipart(
  options: UploadClientOptions,
  params: UploadAssetParams,
): Promise<UploadAssetResult> {
  return new Promise((resolve, reject) => {
    const formData = new FormData();
    formData.append("assetType", params.assetType);
    formData.append("title", params.title);
    formData.append("file", params.file, params.file.name);
    if (params.summary) formData.append("summary", params.summary);
    if (params.projectId) formData.append("projectId", params.projectId);
    if (params.folderId) formData.append("folderId", params.folderId);

    const xhr = new XMLHttpRequest();
    xhr.open("POST", buildUrl(options.baseUrl, "/api/v1/assets/upload"));
    const headers = buildUploadHeaders(options);
    Object.entries(headers).forEach(([key, value]) => xhr.setRequestHeader(key, value));

    xhr.upload.onprogress = (event) => {
      if (!params.onProgress || !event.lengthComputable) return;
      params.onProgress(Math.round((event.loaded / event.total) * 100));
    };

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(parseUploadResponse(xhr));
        } catch (error) {
          reject(isApiError(error) ? error : mapTransportError(error));
        }
        return;
      }
      let body: unknown = xhr.responseText;
      try {
        body = JSON.parse(xhr.responseText);
      } catch {
        // keep raw text
      }
      reject(mapTransportError(new ApiError("Upload failed", "unknown", xhr.status, body)));
    };

    xhr.onerror = () => reject(mapTransportError(new Error("Network error during upload")));
    xhr.onabort = () => reject(mapTransportError(new DOMException("Upload cancelled", "AbortError")));

    if (params.signal) {
      if (params.signal.aborted) {
        xhr.abort();
        return;
      }
      params.signal.addEventListener("abort", () => xhr.abort(), { once: true });
    }

    xhr.send(formData);
  });
}

const POLL_INTERVAL_MS = 1_500;
const POLL_TIMEOUT_MS = 120_000;

export async function pollAssetUntilReady(
  client: ApiClient,
  assetId: string,
  signal?: AbortSignal,
): Promise<AssetDto> {
  const started = Date.now();

  while (Date.now() - started < POLL_TIMEOUT_MS) {
    if (signal?.aborted) {
      throw mapTransportError(new DOMException("Upload cancelled", "AbortError"));
    }

    const response = await client.get<SingleSuccessEnvelope<AssetDto>>(`/api/v1/assets/${assetId}`, {
      signal,
    });
    const asset = response.data.data;
    const scanStatus = asset.media?.scanStatus;

    if (scanStatus === "clean" || scanStatus === "infected" || scanStatus === "failed") {
      if (scanStatus === "failed" || scanStatus === "infected") {
        throw new ApiError("Upload processing failed", "validation_error", 422, asset);
      }
      return asset;
    }

    await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
  }

  throw new ApiError("Upload processing timed out", "timeout", 504);
}

export function createUploadClient(client: ApiClient, baseUrl: string): {
  uploadAsset(params: UploadAssetParams): Promise<AssetDto>;
} {
  const xhrOptions: UploadClientOptions = { baseUrl };

  return {
    async uploadAsset(params: UploadAssetParams): Promise<AssetDto> {
      const accepted = await uploadAssetMultipart(xhrOptions, params);
      const assetId = accepted.operation.resourceId ?? accepted.asset.id;
      const asset = await pollAssetUntilReady(client, assetId, params.signal);
      return asset;
    },
  };
}
