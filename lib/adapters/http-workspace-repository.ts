import type { ApiClient } from "@/lib/api/client";
import type { WorkspaceEnvelope } from "@/lib/api/workspace-types";
import type { WorkspaceRepository } from "@/lib/domain/repositories";
import { mapWorkspaceDto } from "@/lib/settings/mappers";
import type { ProfileState } from "@/lib/settings/mappers";

type HttpWorkspaceRepositoryOptions = {
  readonly getProfile?: () => Promise<ProfileState>;
  readonly getUnreadCount?: () => Promise<number>;
};

export function createHttpWorkspaceRepository(
  client: ApiClient,
  options: HttpWorkspaceRepositoryOptions = {},
): WorkspaceRepository {
  return {
    async getWorkspace() {
      const response = await client.get<WorkspaceEnvelope>("/api/v1/workspace");
      return mapWorkspaceDto(response.data.data);
    },

    async getCurrentUser() {
      if (options.getProfile) {
        const profile = await options.getProfile();
        return {
          name: profile.fullName,
          email: profile.email,
          role: "Member",
        };
      }
      return { name: "Member", email: "", role: "Member" };
    },

    async getUnreadNotificationCount() {
      if (options.getUnreadCount) {
        return options.getUnreadCount();
      }
      const response = await client.get<
        import("@/lib/api/asset-types").PagedSuccessEnvelope<unknown>
      >("/api/v1/notifications?read=false&limit=100");
      return response.data.data.length;
    },
  };
}
