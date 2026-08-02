import { expect, test } from "@playwright/test";

import { ROUTES } from "../fixtures/routes";

test.describe("route navigation", () => {
  for (const href of Object.values(ROUTES)) {
    test(`loads ${href} with primary navigation`, async ({ page }) => {
      await page.goto(href);
      await expect(page.getByRole("navigation", { name: "Primary" })).toBeVisible();
      await expect(page.locator("main")).toBeVisible();
    });
  }

  test("toggles theme from the header control", async ({ page }) => {
    await page.goto(ROUTES.dashboard);

    const toggle = page.getByRole("button", { name: /Switch to (light|dark) theme/i });
    await expect(toggle).toBeVisible();

    const wasDark = await page.evaluate(() => document.documentElement.classList.contains("dark"));
    await toggle.click();
    const isDark = await page.evaluate(() => document.documentElement.classList.contains("dark"));
    expect(isDark).not.toBe(wasDark);
  });

  test("shows sidebar navigation on desktop viewport", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto(ROUTES.dashboard);

    await expect(page.getByRole("navigation", { name: "Primary" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Dashboard" })).toBeVisible();
  });
});
