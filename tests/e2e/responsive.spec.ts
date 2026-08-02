import { devices, expect, test } from "@playwright/test";

import { ROUTES } from "../fixtures/routes";

test.use({ ...devices["iPhone 13"] });

test.describe("responsive behavior", () => {
  test("opens mobile navigation from the dashboard", async ({ page }) => {
    await page.goto(ROUTES.dashboard);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

    const menuButton = page.getByRole("button", { name: /Open navigation/i });
    await expect(menuButton).toBeVisible();
    await menuButton.click();
    await expect(page.getByRole("button", { name: /Close navigation/i })).toBeVisible();
    await expect(page.getByRole("navigation", { name: "Primary" })).toBeVisible();
  });

  test("content library remains usable on tablet width", async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto(ROUTES.contentLibrary);
    await expect(page.getByRole("searchbox")).toBeVisible();
    await expect(page.locator("main")).toBeVisible();
  });

  test("collapses breadcrumb intermediates on narrow viewports", async ({ page }) => {
    await page.goto(ROUTES.contentLibrary);
    const breadcrumb = page.getByRole("navigation", { name: "Breadcrumb" });
    await expect(breadcrumb).toBeVisible();
  });
});
