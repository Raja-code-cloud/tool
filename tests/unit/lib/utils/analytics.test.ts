import { describe, expect, it } from "vitest";

import { formatCompactNumber, formatPercent } from "@/lib/utils/analytics";

describe("analytics formatting utilities", () => {
  it("formats compact numbers with analytics preset", () => {
    expect(formatCompactNumber(12500)).toMatch(/12\.?5K|12K/);
    expect(formatCompactNumber(42)).toMatch(/42/);
  });

  it("formats percent values for chart labels", () => {
    expect(formatPercent(42.5)).toMatch(/42\.5%/);
  });
});
