import { expect, test } from "@playwright/test";

test("Playwright creates an isolated browser page", async ({ page }) => {
  await page.setContent("<main><h1>Testing foundation ready</h1></main>");

  await expect(page.getByRole("heading", { name: "Testing foundation ready" })).toBeVisible();
});
