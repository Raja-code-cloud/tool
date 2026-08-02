import { describe, expect, it } from "vitest";

import { mapAssetDtoToContentItem, mapStatusToLifecycle } from "@/lib/content/mappers";

describe("content mappers", () => {
  it("maps backend asset lifecycle to frontend content status", () => {
    const item = mapAssetDtoToContentItem({
      id: "asset-1",
      version: 2,
      createdAt: "2026-01-01T00:00:00.000Z",
      updatedAt: "2026-01-02T00:00:00.000Z",
      assetType: "poster",
      title: "Launch poster",
      summary: "Hero visual",
      lifecycleStatus: "active",
      ownerId: "user-1",
      projectId: "project-1",
      folderId: null,
      isFavorite: true,
      tagIds: ["tag-1"],
      media: {
        mimeType: "image/png",
        byteSize: 1024,
        checksumSha256: "abc",
        scanStatus: "clean",
        filename: "poster.png",
        extractedMetadata: {},
        downloadUrl: "https://example.test/poster.png",
      },
    });

    expect(item.status).toBe("published");
    expect(item.type).toBe("poster");
    expect(item.version).toBe(2);
    expect(item.downloadUrl).toBe("https://example.test/poster.png");
  });

  it("maps frontend status back to backend lifecycle", () => {
    expect(mapStatusToLifecycle("published")).toBe("active");
    expect(mapStatusToLifecycle("scheduled")).toBeNull();
  });
});
