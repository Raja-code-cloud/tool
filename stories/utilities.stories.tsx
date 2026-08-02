import type { Meta, StoryObj } from "@storybook/react";
import * as React from "react";

import { VisuallyHidden } from "../components/common";
import {
  FilterBar,
  FilterChip,
  FilterGroup,
  FilterSearch,
  FilterSelect,
} from "../components/filters";
import { ThemeToggle } from "../components/theme/theme-toggle";
import {
  Button,
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../components/ui";

const meta = {
  title: "Utilities/Filters Menus and Theme",
  component: FilterBar,
  parameters: {
    docs: {
      description: {
        component:
          "Cross-cutting filter, menu, visually-hidden, and theme utilities. Controls retain names, keyboard interaction, focus management, and responsive wrapping.",
      },
    },
  },
} satisfies Meta<typeof FilterBar>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Filters: Story = {
  render: function ControlledFilters() {
    const [status, setStatus] = React.useState("all");
    return (
      <FilterBar>
        <FilterSearch placeholder="Search results" />
        <FilterGroup label="Filter options">
          <FilterSelect
            id="filter-status"
            label="Status"
            value={status}
            onValueChange={setStatus}
            options={[
              { value: "all", label: "All statuses" },
              { value: "draft", label: "Draft" },
              { value: "published", label: "Published" },
            ]}
          />
          <FilterChip label="Last 30 days" onRemove={() => undefined} />
        </FilterGroup>
      </FilterBar>
    );
  },
  parameters: {
    docs: {
      description: {
        story:
          "FilterBar, FilterGroup, FilterSearch, FilterSelect, and FilterChip wrap on compact screens and expose group/control labels.",
      },
    },
  },
};

export const DropdownMenuFamily: Story = {
  render: function ControlledCheckboxItem() {
    const [checked, setChecked] = React.useState(true);
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="secondary">Open menu</Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuLabel className="px-3 py-2 font-semibold">View options</DropdownMenuLabel>
          <DropdownMenuItem>Edit</DropdownMenuItem>
          <DropdownMenuCheckboxItem checked={checked} onCheckedChange={setChecked}>
            Show archived
          </DropdownMenuCheckboxItem>
          <DropdownMenuSeparator className="bg-border my-1 h-px" />
          <DropdownMenuItem isDestructive>Delete</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    );
  },
  parameters: {
    docs: {
      description: {
        story:
          "DropdownMenu, Trigger, Content, Label, Item, CheckboxItem, and Separator provide roving keyboard focus and portal-based positioning.",
      },
    },
  },
};

export const ThemeAndAssistiveUtilities: Story = {
  render: () => (
    <div className="flex items-center gap-3">
      <ThemeToggle />
      <span>Use the toolbar theme global or this toggle.</span>
      <VisuallyHidden>Additional screen-reader-only context.</VisuallyHidden>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "ThemeToggle uses the ThemeProvider and switches token-based light/dark appearance. VisuallyHidden preserves assistive text without visual layout.",
      },
    },
  },
};
