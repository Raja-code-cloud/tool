import { describe, expect, it, vi } from "vitest";

import { formatDuration, readTextFile, readVideoDuration } from "@/lib/utils/upload-wizard";

describe("upload wizard utilities", () => {
  it("formats durations as mm:ss", () => {
    expect(formatDuration(65)).toBe("1:05");
    expect(formatDuration(9)).toBe("0:09");
  });

  it("reads text file contents", async () => {
    const file = new File(["# Hello"], "article.md", { type: "text/markdown" });
    Object.defineProperty(file, "text", {
      value: vi.fn().mockResolvedValue("# Hello"),
    });

    await expect(readTextFile(file)).resolves.toBe("# Hello");
  });

  it("returns a fallback when video metadata cannot be loaded", async () => {
    vi.spyOn(URL, "createObjectURL").mockReturnValue("blob:invalid");
    vi.spyOn(URL, "revokeObjectURL").mockImplementation(() => undefined);
    vi.spyOn(document, "createElement").mockImplementation((tagName: string) => {
      if (tagName !== "video") {
        return document.createElement.bind(document)(tagName);
      }

      const video = {
        preload: "",
        onloadedmetadata: null as (() => void) | null,
        onerror: null as ((event: Event) => void) | null,
        set src(_value: string) {
          this.onerror?.(new Event("error"));
        },
      };

      return video as unknown as HTMLVideoElement;
    });

    const file = new File(["video"], "clip.mp4", { type: "video/mp4" });
    await expect(readVideoDuration(file)).resolves.toBe("—");
  });
});
