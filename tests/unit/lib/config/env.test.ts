import { describe, expect, it } from "vitest";

import { env, isDev, isProd, isTest } from "@/lib/config/env";

describe("environment module", () => {
  it("exposes validated public environment values", () => {
    expect(["development", "test", "production"]).toContain(env.NODE_ENV);
    expect(["development", "staging", "production"]).toContain(env.NEXT_PUBLIC_APP_ENV);
  });

  it("derives runtime mode helpers from NODE_ENV", () => {
    expect(typeof isDev).toBe("boolean");
    expect(typeof isProd).toBe("boolean");
    expect(typeof isTest).toBe("boolean");
    expect(isDev || isProd || isTest).toBe(true);
  });
});
