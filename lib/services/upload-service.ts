import type { AssetDto } from "@/lib/api/asset-types";
import type { ApiClient } from "@/lib/api/client";
import { createUploadClient, type UploadAssetParams } from "@/lib/api/upload-client";
import type { ContentType } from "@/lib/domain/content";

export type UploadRepository = {
  uploadAsset(params: UploadAssetParams): Promise<AssetDto>;
};

export type CreateProjectParams = {
  readonly projectId: string;
  readonly projectName: string;
  readonly description: string;
  readonly category: string;
  readonly tags: string;
  readonly posterFile?: File | null;
  readonly articleFile?: File | null;
  readonly articleContent?: string;
  readonly videoFile?: File | null;
  readonly thumbnailFile?: File | null;
  readonly onAssetProgress?: (kind: ContentType, percent: number) => void;
  readonly signal?: AbortSignal;
};

export type CreateProjectResult = {
  readonly projectId: string;
  readonly assets: readonly AssetDto[];
};

function articleFileFromContent(content: string, projectName: string): File {
  const blob = new Blob([content], { type: "text/plain" });
  const safeName = projectName.trim().replace(/\s+/g, "-").slice(0, 80) || "article";
  return new File([blob], `${safeName}.txt`, { type: "text/plain" });
}

export function createUploadRepository(client: ApiClient, baseUrl: string): UploadRepository {
  const uploadClient = createUploadClient(client, baseUrl);
  return {
    uploadAsset: (params) => uploadClient.uploadAsset(params),
  };
}

export function createUploadService(repository: UploadRepository) {
  return {
    uploadAsset: (params: UploadAssetParams) => repository.uploadAsset(params),

    async createProject(params: CreateProjectParams): Promise<CreateProjectResult> {
      const assets: AssetDto[] = [];
      const summary = [params.description, params.category ? `Category: ${params.category}` : ""]
        .filter(Boolean)
        .join("\n\n");
      const metadataTags = params.tags.trim();

      if (params.posterFile) {
        assets.push(
          await repository.uploadAsset({
            assetType: "poster",
            title: `${params.projectName} — Poster`,
            summary,
            file: params.posterFile,
            projectId: params.projectId,
            signal: params.signal,
            onProgress: (percent) => params.onAssetProgress?.("poster", percent),
          }),
        );
      }

      const articleFile =
        params.articleFile ??
        (params.articleContent?.trim()
          ? articleFileFromContent(params.articleContent, params.projectName)
          : null);

      if (articleFile) {
        assets.push(
          await repository.uploadAsset({
            assetType: "article",
            title: `${params.projectName} — Article`,
            summary: metadataTags ? `${summary}\n\nTags: ${metadataTags}` : summary,
            file: articleFile,
            projectId: params.projectId,
            signal: params.signal,
            onProgress: (percent) => params.onAssetProgress?.("article", percent),
          }),
        );
      }

      if (params.videoFile) {
        assets.push(
          await repository.uploadAsset({
            assetType: "video",
            title: `${params.projectName} — Video`,
            summary,
            file: params.videoFile,
            projectId: params.projectId,
            signal: params.signal,
            onProgress: (percent) => params.onAssetProgress?.("video", percent),
          }),
        );
      }

      if (params.thumbnailFile) {
        assets.push(
          await repository.uploadAsset({
            assetType: "thumbnail",
            title: `${params.projectName} — Thumbnail`,
            summary,
            file: params.thumbnailFile,
            projectId: params.projectId,
            signal: params.signal,
            onProgress: (percent) => params.onAssetProgress?.("thumbnail", percent),
          }),
        );
      }

      return { projectId: params.projectId, assets };
    },
  };
}

export type UploadService = ReturnType<typeof createUploadService>;
