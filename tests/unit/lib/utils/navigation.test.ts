import { describe, expect, it } from "vitest";

import { NAV_ROUTES, ROUTES } from "@/constants/navigation";
import { buildBreadcrumbs, buildRouteMetadata, isRouteActive } from "@/lib/utils/navigation";

describe("navigation utilities", () => {
  it("builds breadcrumbs from known routes with home ancestor", () => {
    expect(buildBreadcrumbs(ROUTES.contentLibrary)).toEqual([
      { label: "Home", href: ROUTES.dashboard },
      { label: "Content Library", href: ROUTES.contentLibrary },
    ]);
  });

  it("starts at dashboard without a redundant Home crumb", () => {
    expect(buildBreadcrumbs(ROUTES.dashboard)).toEqual([
      { label: "Dashboard", href: ROUTES.dashboard },
    ]);
  });

  it("humanizes unknown nested segments", () => {
    expect(buildBreadcrumbs("/settings/profile")).toEqual([
      { label: "Home", href: ROUTES.dashboard },
      { label: "Settings", href: ROUTES.settings },
      { label: "Profile", href: "/settings/profile" },
    ]);
  });

  it("returns a home-only trail for the root path", () => {
    expect(buildBreadcrumbs("/")).toEqual([{ label: "Home" }]);
  });

  it("derives metadata from navigation constants", () => {
    expect(buildRouteMetadata(ROUTES.upload)).toEqual({
      title: "Upload Wizard",
      description: "Guided multi-step upload and enrichment flow.",
    });
    expect(buildRouteMetadata("/unknown")).toEqual({});
  });

  it("detects active routes including nested paths", () => {
    expect(isRouteActive("/content-library/cl-1", ROUTES.contentLibrary)).toBe(true);
    expect(isRouteActive("/content-library", ROUTES.contentLibrary)).toBe(true);
    expect(isRouteActive("/settings", ROUTES.dashboard)).toBe(false);
  });

  it("aligns breadcrumb terminal labels with every sidebar route", () => {
    for (const route of NAV_ROUTES) {
      const crumbs = buildBreadcrumbs(route.href);
      expect(crumbs.at(-1)).toEqual({ label: route.label, href: route.href });
    }
  });
});
