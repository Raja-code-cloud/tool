import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { server } from "../mocks/server";

describe("MSW foundation", () => {
  it("intercepts requests registered by a test", async () => {
    server.use(http.get("https://test.local/health", () => HttpResponse.json({ status: "ok" })));

    const response = await fetch("https://test.local/health");
    await expect(response.json()).resolves.toEqual({ status: "ok" });
  });

  it("fails on unhandled requests outside explicit handlers", async () => {
    server.use(http.get("https://test.local/allowed", () => HttpResponse.json({ ok: true })));

    await expect(fetch("https://test.local/allowed")).resolves.toMatchObject({ ok: true });
  });
});
