import type { PagedSuccessEnvelope, SingleSuccessEnvelope } from "@/lib/api/asset-types";
import type { ApiClient } from "@/lib/api/client";
import type {
  CreateScheduleRequestDto,
  DispatchPublicationRequestDto,
  ScheduleCalendarDto,
  ScheduleDto,
  UpdateScheduleRequestDto,
} from "@/lib/api/scheduler-types";
import type {
  CreateScheduleInput,
  ListSchedulesFilters,
  SchedulerRepository,
  UpdateScheduleInput,
} from "@/lib/domain/repositories";
import { mapScheduleCalendarDto, mapScheduleDto } from "@/lib/scheduler/mappers";

function createIdempotencyKey(prefix: string): string {
  return `${prefix}-${globalThis.crypto?.randomUUID?.() ?? Date.now()}`;
}

function buildScheduleQuery(filters: ListSchedulesFilters = {}): string {
  const search = new URLSearchParams();
  if (filters.cursor) search.set("cursor", filters.cursor);
  if (filters.limit) search.set("limit", String(filters.limit));
  filters.state?.forEach((value) => search.append("state", value));
  filters.priority?.forEach((value) => search.append("priority", value));
  if (filters.scheduledAfter) search.set("scheduledAfter", filters.scheduledAfter);
  if (filters.scheduledBefore) search.set("scheduledBefore", filters.scheduledBefore);
  if (filters.sort) search.set("sort", filters.sort);
  const query = search.toString();
  return query ? `?${query}` : "";
}

async function fetchAllSchedules(
  client: ApiClient,
  filters: ListSchedulesFilters = {},
): Promise<readonly ScheduleCalendarDto[]> {
  const items: ScheduleCalendarDto[] = [];
  let cursor = filters.cursor;
  let hasMore = true;

  while (hasMore) {
    const path = `/api/v1/schedule${buildScheduleQuery({ ...filters, cursor, limit: filters.limit ?? 100 })}`;
    const response = await client.get<PagedSuccessEnvelope<ScheduleCalendarDto>>(path);
    items.push(...response.data.data);
    const page = response.data.meta?.page;
    cursor = page?.nextCursor ?? undefined;
    hasMore = page?.hasMore ?? false;
    if (!page?.hasMore) break;
  }

  return items;
}

export function createHttpSchedulerRepository(client: ApiClient): SchedulerRepository {
  return {
    async listPosts(filters?: ListSchedulesFilters) {
      const schedules = await fetchAllSchedules(client, filters);
      return schedules.map(mapScheduleCalendarDto);
    },

    listNotifications() {
      return [];
    },

    async getSchedule(id: string) {
      const response = await client.get<SingleSuccessEnvelope<ScheduleDto>>(`/api/v1/schedule/${id}`);
      return mapScheduleDto(response.data.data);
    },

    async createSchedule(input: CreateScheduleInput) {
      const body: CreateScheduleRequestDto = {
        publicationTargetId: input.publicationTargetId,
        requestedLocalAt: input.requestedLocalAt,
        timeZone: input.timeZone,
        priority: input.priority,
        ambiguityPolicy: input.ambiguityPolicy,
        fold: input.fold,
      };
      const response = await client.post<SingleSuccessEnvelope<ScheduleDto>>(
        "/api/v1/schedule",
        body,
        { headers: { "Idempotency-Key": createIdempotencyKey("schedule-create") } },
      );
      return mapScheduleDto(response.data.data);
    },

    async updateSchedule(id: string, version: number, input: UpdateScheduleInput) {
      const body: UpdateScheduleRequestDto = {
        requestedLocalAt: input.requestedLocalAt,
        timeZone: input.timeZone,
        priority: input.priority,
        ambiguityPolicy: input.ambiguityPolicy,
        fold: input.fold,
        state: input.state,
      };
      const response = await client.patch<SingleSuccessEnvelope<ScheduleDto>>(
        `/api/v1/schedule/${id}`,
        body,
        { headers: { "If-Match": String(version) } },
      );
      return mapScheduleDto(response.data.data);
    },

    async cancelSchedule(id: string, version: number) {
      const response = await client.delete<SingleSuccessEnvelope<ScheduleDto>>(
        `/api/v1/schedule/${id}`,
        { headers: { "If-Match": String(version) } },
      );
      return mapScheduleDto(response.data.data);
    },

    async dispatchPublication(publicationId: string, version: number, targetIds?: readonly string[]) {
      const body: DispatchPublicationRequestDto | undefined = targetIds?.length
        ? { targetIds }
        : undefined;
      await client.post(`/api/v1/publish/${publicationId}`, body, {
        headers: {
          "If-Match": String(version),
          "Idempotency-Key": createIdempotencyKey("publish-dispatch"),
        },
      });
    },

    async cancelPublication(publicationId: string, version: number) {
      await client.delete(`/api/v1/publish/${publicationId}`, {
        headers: { "If-Match": String(version) },
      });
    },

    async retryPublication(publicationId: string, version: number, targetIds?: readonly string[]) {
      await this.dispatchPublication(publicationId, version, targetIds);
    },
  };
}

export function createMockSchedulerRepository(
  posts: readonly import("@/lib/domain/scheduler").ScheduledPost[],
  notifications: readonly import("@/lib/domain/scheduler").SchedulerNotification[],
): SchedulerRepository {
  let store = posts.map((post, index) => ({
    ...post,
    version: post.version ?? 1,
    publicationTargetId: post.publicationTargetId ?? `target-${index + 1}`,
  }));

  return {
    async listPosts() {
      return store;
    },

    listNotifications() {
      return notifications;
    },

    async getSchedule(id: string) {
      const post = store.find((entry) => entry.id === id);
      if (!post) throw new Error("Schedule not found");
      return post;
    },

    async createSchedule(input) {
      const created = {
        id: `sch-${Date.now()}`,
        version: 1,
        publicationTargetId: input.publicationTargetId,
        title: "New schedule",
        platforms: ["linkedin" as const],
        scheduledAt: new Date(input.requestedLocalAt).toISOString(),
        timezone: input.timeZone,
        status: "scheduled" as const,
        priority: input.priority ?? ("normal" as const),
        thumbnailHue: 180,
        aiVersion: "v1.0",
        approvalStatus: "pending" as const,
        queueOrder: store.length + 1,
        hasContent: true,
      };
      store = [...store, created];
      return created;
    },

    async updateSchedule(id, version, input) {
      const index = store.findIndex((entry) => entry.id === id);
      if (index < 0) throw new Error("Schedule not found");
      const current = store[index]!;
      const updated = {
        ...current,
        version: version + 1,
        scheduledAt: input.requestedLocalAt
          ? new Date(input.requestedLocalAt).toISOString()
          : current.scheduledAt,
        timezone: input.timeZone ?? current.timezone,
        priority: input.priority ?? current.priority,
      };
      store = [...store.slice(0, index), updated, ...store.slice(index + 1)];
      return updated;
    },

    async cancelSchedule(id, version) {
      const index = store.findIndex((entry) => entry.id === id);
      if (index < 0) throw new Error("Schedule not found");
      const updated = { ...store[index]!, status: "cancelled" as const, version: version + 1 };
      store = [...store.slice(0, index), updated, ...store.slice(index + 1)];
      return updated;
    },

    async dispatchPublication(publicationId) {
      store = store.map((post) =>
        post.publicationId === publicationId ? { ...post, status: "publishing" as const } : post,
      );
    },

    async cancelPublication(publicationId) {
      store = store.map((post) =>
        post.publicationId === publicationId ? { ...post, status: "cancelled" as const } : post,
      );
    },

    async retryPublication(publicationId, version) {
      await this.dispatchPublication(publicationId, version);
    },
  };
}
