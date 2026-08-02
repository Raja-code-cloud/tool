import { describe, expect, it, vi } from "vitest";

import { FilterBar, FilterChip, FilterSelect } from "@/components/filters/filters";
import { renderWithProviders, screen } from "@/tests/utils";

describe("filter components", () => {
  it("renders an accessible filter bar with select and removable chips", async () => {
    const onRemove = vi.fn();
    const onValueChange = vi.fn();
    const { user } = renderWithProviders(
      <FilterBar>
        <FilterSelect
          id="status-filter"
          label="Status"
          value="all"
          onValueChange={onValueChange}
          options={[
            { value: "all", label: "All statuses" },
            { value: "draft", label: "Draft" },
          ]}
        />
        <FilterChip label="Draft" onRemove={onRemove} />
      </FilterBar>,
    );

    expect(screen.getByRole("region", { name: "Filters" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Remove filter" }));
    expect(onRemove).toHaveBeenCalledOnce();
  });
});
