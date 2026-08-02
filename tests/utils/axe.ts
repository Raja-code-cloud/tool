import { expect } from "vitest";
import { axe } from "vitest-axe";

export { axe };

export async function expectNoCriticalViolations(container: Element): Promise<void> {
  const results = await axe(container);
  const critical = results.violations.filter(
    (violation) => violation.impact === "critical" || violation.impact === "serious",
  );
  expect(critical).toEqual([]);
}
