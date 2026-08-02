import { describe, expect, it } from "vitest";

import { NAV_ROUTES, ROUTES as APP_ROUTES } from "@/constants/navigation";
import { buildBreadcrumbs, buildRouteMetadata } from "@/lib/utils/navigation";
import { ROUTES } from "../fixtures/routes";

describe("routing workflow", () => {
  it("exports route constants aligned with the application", () => {
    expect(ROUTES).toEqual(APP_ROUTES);
    expect(Object.values(ROUTES)).toHaveLength(NAV_ROUTES.length);
  });

  it("derives metadata for every navigable route", () => {
    for (const route of NAV_ROUTES) {
      expect(buildRouteMetadata(route.href)).toEqual({
        title: route.label,
        description: route.description,
      });
    }
  });

  it("builds breadcrumbs whose terminal label matches the sidebar", () => {
    for (const route of NAV_ROUTES) {
      const crumbs = buildBreadcrumbs(route.href);
      expect(crumbs.at(-1)).toEqual({ label: route.label, href: route.href });
    }
  });

  it("uses dashboard as the workspace root without a redundant Home crumb", () => {
    expect(buildBreadcrumbs(ROUTES.dashboard)).toEqual([
      { label: "Dashboard", href: ROUTES.dashboard },
    ]);
  });

  it("prefixes non-dashboard routes with a Home link to the dashboard", () => {
    for (const route of NAV_ROUTES) {
      if (route.href === ROUTES.dashboard) continue;
      const crumbs = buildBreadcrumbs(route.href);
      expect(crumbs[0]).toEqual({ label: "Home", href: ROUTES.dashboard });
    }
  });
});
