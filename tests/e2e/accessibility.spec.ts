import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

import { ROUTES } from "../fixtures/routes";

test("dashboard has no serious accessibility violations", async ({ page }) => {
  await page.goto(ROUTES.dashboard);
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

  const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();

  const critical = results.violations.filter(
    (violation) => violation.impact === "critical" || violation.impact === "serious",
  );
  expect(critical).toEqual([]);
});
