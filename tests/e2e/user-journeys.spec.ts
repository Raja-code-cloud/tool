import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

import { ROUTES } from "../fixtures/routes";

test.describe("dashboard journey", () => {
  test("loads dashboard metrics and navigation shell", async ({ page }) => {
    await page.goto(ROUTES.dashboard);
    await expect(page.getByRole("heading", { level: 1 })).toContainText(
      /good (morning|afternoon|evening)/i,
    );
    await expect(page.getByRole("navigation", { name: "Primary" })).toBeVisible();
    await expect(page.getByText(/recent content|ai suggestions|publishing/i).first()).toBeVisible();
  });
});

test.describe("content library journey", () => {
  test("filters and searches library content", async ({ page }) => {
    await page.goto(ROUTES.contentLibrary);
    await expect(page.getByRole("heading", { level: 1 })).toContainText(/content library/i);
    await page.getByRole("searchbox", { name: "Search content library" }).fill("terraform");
    await expect(page.getByText(/terraform/i).first()).toBeVisible();
  });
});

test.describe("upload journeys", () => {
  test("starts article upload wizard", async ({ page }) => {
    await page.goto(ROUTES.upload);
    await expect(page.getByRole("heading", { level: 1 })).toContainText(/upload/i);
    await expect(page.getByLabel(/project name/i)).toBeVisible();
    await page.getByLabel(/project name/i).fill("Azure Landing Zone Guide");
    await expect(page.getByRole("button", { name: /next|continue/i })).toBeVisible();
  });
});

test.describe("ai studio journey", () => {
  test("opens generation workspace", async ({ page }) => {
    await page.goto(ROUTES.aiStudio);
    await expect(page.getByRole("heading", { level: 1 })).toContainText(/ai studio/i);
    await expect(page.getByText(/generate|prompt|provider/i).first()).toBeVisible();
  });
});

test.describe("scheduler journey", () => {
  test("shows calendar and publishing queue", async ({ page }) => {
    await page.goto(ROUTES.scheduler);
    await expect(page.getByRole("heading", { level: 1 })).toContainText(/scheduler/i);
    await expect(page.getByText(/queue|calendar|scheduled/i).first()).toBeVisible();
  });
});

test.describe("settings journey", () => {
  test("loads editable settings sections", async ({ page }) => {
    await page.goto(ROUTES.settings);
    await expect(page.getByRole("heading", { level: 1 })).toContainText(/settings/i);
    await expect(page.getByText(/profile|notifications|providers/i).first()).toBeVisible();
  });
});

test.describe("theme and keyboard behavior", () => {
  test("supports dark mode toggle without breaking layout", async ({ page }) => {
    await page.goto(ROUTES.dashboard);
    const themeToggle = page.getByRole("button", { name: /switch to (light|dark) theme/i });
    await themeToggle.click();
    await expect(page.locator("html")).toHaveAttribute("class", /.+/);
  });

  test("allows keyboard navigation through primary sidebar links", async ({ page }) => {
    await page.goto(ROUTES.dashboard);
    await page.keyboard.press("Tab");
    const focused = page.locator(":focus");
    await expect(focused).toBeVisible();
  });
});

test.describe("accessibility", () => {
  test("dashboard has no critical axe violations", async ({ page }) => {
    await page.goto(ROUTES.dashboard);
    const results = await new AxeBuilder({ page }).analyze();
    const critical = results.violations.filter(
      (violation) => violation.impact === "critical" || violation.impact === "serious",
    );
    expect(critical).toEqual([]);
  });
});
