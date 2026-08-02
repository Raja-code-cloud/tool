import type {
  AssetDto,
  PagedSuccessEnvelope,
  SingleSuccessEnvelope,
  UpdateContentRequestDto,
} from "@/lib/api/asset-types";
import type { ApiClient } from "@/lib/api/client";
import { ApiError } from "@/lib/api/errors";
import { mapAssetDtoToContentItem, mapStatusToLifecycle } from "@/lib/content/mappers";
import type {
  ContentListParams,
  ContentListResult,
  ContentRepository,
  ContentUpdateInput,
} from "@/lib/domain/repositories";

function buildQuery(params: ContentListParams): string {
  const search = new URLSearchParams();
  if (params.cursor) search.set("cursor", params.cursor);
  if (params.limit) search.set("limit", String(params.limit));
  params.assetTypes?.forEach((type) => search.append("assetType", type));
  params.lifecycleStatuses?.forEach((status) => search.append("lifecycleStatus", status));
  if (params.sort) search.set("sort", params.sort);
  if (params.projectId) search.set("projectId", params.projectId);
  const query = search.toString();
  return query ? `?${query}` : "";
}

function mapUpdateInput(input: ContentUpdateInput): UpdateContentRequestDto {
  const lifecycle = input.lifecycleStatus ? mapStatusToLifecycle(input.lifecycleStatus) : undefined;
  return {
    title: input.title,
    summary: input.summary,
    bodyText: input.bodyText,
    metadata: input.metadata,
    lifecycleStatus: lifecycle ?? undefined,
  };
}

export function createHttpContentRepository(client: ApiClient): ContentRepository {
  return {
    async list(params: ContentListParams = {}): Promise<ContentListResult> {
      const useSearch = params.query && params.query.trim().length >= 2;
      const path = useSearch
        ? `/api/v1/assets/search?${new URLSearchParams({
            q: params.query!.trim(),
            ...(params.limit ? { limit: String(params.limit) } : {}),
            ...(params.sort ? { sort: params.sort } : {}),
          }).toString()}`
        : `/api/v1/assets${buildQuery(params)}`;

      const response = await client.get<PagedSuccessEnvelope<AssetDto>>(path);
      const page = response.data.meta?.page;

      return {
        items: response.data.data.map(mapAssetDtoToContentItem),
        nextCursor: page?.nextCursor ?? null,
        hasMore: page?.hasMore ?? false,
      };
    },

    async getById(id: string) {
      const response = await client.get<SingleSuccessEnvelope<AssetDto>>(`/api/v1/assets/${id}`);
      return mapAssetDtoToContentItem(response.data.data);
    },

    async delete(id: string, version: number): Promise<void> {
      await client.delete<void>(`/api/v1/assets/${id}`, {
        headers: { "If-Match": String(version) },
      });
    },

    async archive(_id: string, _version: number) {
      throw new ApiError(
        "Asset archive is not yet available via the backend API. Use delete or contact support.",
        "unknown",
        501,
      );
    },

    async update(_id: string, _version: number, _input: ContentUpdateInput) {
      throw new ApiError(
        "Asset metadata edit is not yet available via the backend API.",
        "unknown",
        501,
      );
    },
  };
}

export function createMockContentRepository(
  items: readonly import("@/lib/domain/content").ContentItem[],
): ContentRepository {
  let store = [...items];

  return {
    async list(params: ContentListParams = {}): Promise<ContentListResult> {
      let result = [...store];
      if (params.assetTypes?.length) {
        result = result.filter((item) => params.assetTypes!.includes(item.type));
      }
      if (params.lifecycleStatuses?.length) {
        result = result.filter((item) => {
          const lifecycle = mapStatusToLifecycle(item.status);
          return lifecycle !== null && params.lifecycleStatuses!.includes(lifecycle);
        });
      }
      if (params.query) {
        const query = params.query.toLowerCase();
        result = result.filter(
          (item) =>
            item.title.toLowerCase().includes(query) ||
            item.summary.toLowerCase().includes(query) ||
            item.tags.some((tag) => tag.toLowerCase().includes(query)),
        );
      }
      const limit = params.limit ?? result.length;
      const slice = result.slice(0, limit);
      return { items: slice, nextCursor: null, hasMore: result.length > limit };
    },

    async getById(id: string) {
      const item = store.find((entry) => entry.id === id);
      if (!item) throw new ApiError("Not found", "not_found", 404);
      return item;
    },

    async delete(id: string, _version: number) {
      store = store.filter((entry) => entry.id !== id);
    },

    async archive(id: string, version: number) {
      const index = store.findIndex((entry) => entry.id === id);
      if (index < 0) throw new ApiError("Not found", "not_found", 404);
      const updated = { ...store[index]!, status: "archived" as const, version: version + 1 };
      store = [...store.slice(0, index), updated, ...store.slice(index + 1)];
      return updated;
    },

    async update(id: string, version: number, input: ContentUpdateInput) {
      const index = store.findIndex((entry) => entry.id === id);
      if (index < 0) throw new ApiError("Not found", "not_found", 404);
      const updated = {
        ...store[index]!,
        title: input.title,
        summary: input.summary ?? store[index]!.summary,
        version: version + 1,
        updatedAt: new Date().toISOString(),
        ...(input.lifecycleStatus ? { status: input.lifecycleStatus } : {}),
      };
      store = [...store.slice(0, index), updated, ...store.slice(index + 1)];
      return updated;
    },
  };
}
