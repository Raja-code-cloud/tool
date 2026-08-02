import type { Meta, StoryObj } from "@storybook/react";
import * as React from "react";

import { AgendaList, CalendarRange, CalendarSingle, DatePicker } from "../components/calendar";
import { AvatarGroup, KeyValueList, Toolbar } from "../components/common";
import { DataTable, EmptyTableState, SortButton, TableToolbar } from "../components/tables";
import { Button } from "../components/ui";

type Row = { id: string; title: string; status: string; reach: number };
const rows: readonly Row[] = [
  { id: "1", title: "Launch", status: "Published", reach: 12400 },
  { id: "2", title: "Update", status: "Draft", reach: 0 },
];
const columns = [
  { id: "title", header: "Title", cell: (row: Row) => row.title, isPrimary: true },
  { id: "status", header: "Status", cell: (row: Row) => row.status },
  {
    id: "reach",
    header: "Reach",
    cell: (row: Row) => row.reach.toLocaleString(),
    align: "right" as const,
  },
];

const meta = {
  title: "Data Display/Tables and Calendar",
  component: DataTable<Row>,
  args: { caption: "Campaign performance", rows, columns, getRowId: (row) => row.id },
  parameters: {
    docs: {
      description: {
        component:
          "Structured data patterns preserve captions, headings, responsive overflow, and meaningful empty states. Calendar controls expose accessible day-picker semantics.",
      },
    },
  },
} satisfies Meta<typeof DataTable<Row>>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Tables: Story = {
  render: () => (
    <div className="grid gap-4">
      <TableToolbar>
        <SortButton direction="ascending">Title</SortButton>
        <Button size="compact">Export</Button>
      </TableToolbar>
      <DataTable
        caption="Campaign performance"
        rows={rows}
        columns={columns}
        getRowId={(row) => row.id}
      />
      <DataTable
        caption="Empty campaigns"
        rows={[]}
        columns={columns}
        getRowId={(row) => row.id}
        empty={
          <EmptyTableState
            title="No campaigns"
            description="Create a campaign to populate this table."
          />
        }
        density="compact"
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "DataTable, SortButton, TableToolbar, and EmptyTableState. The primary column stays visible during horizontal scrolling.",
      },
    },
  },
};

export const Calendars: Story = {
  render: function CalendarStories() {
    const [date, setDate] = React.useState<Date>();
    return (
      <div className="flex flex-wrap items-start gap-6">
        <CalendarSingle {...(date ? { selected: date } : {})} onSelect={setDate} />
        <CalendarRange />
        <DatePicker {...(date ? { value: date } : {})} onChange={setDate} />
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story:
          "CalendarSingle, CalendarRange, and DatePicker support single/range selection, disabled dates, and keyboard day navigation.",
      },
    },
  },
};

export const Agenda: Story = {
  render: () => (
    <AgendaList
      dateLabel="Monday, August 3"
      items={[
        { id: "1", time: "09:00", title: "Planning", meta: "30 minutes", status: "Confirmed" },
        { id: "2", time: "14:30", title: "Review" },
      ]}
    />
  ),
  parameters: {
    docs: {
      description: {
        story:
          "AgendaList presents scheduled items in reading order and accepts a custom empty state.",
      },
    },
  },
};

export const SupportingDataPatterns: Story = {
  render: () => (
    <div className="grid max-w-xl gap-6">
      <AvatarGroup
        items={[
          { id: "1", name: "Ada" },
          { id: "2", name: "Grace" },
          { id: "3", name: "Linus" },
          { id: "4", name: "Margaret" },
        ]}
        maximum={3}
      />
      <Toolbar label="Content actions">
        <Button>Edit</Button>
        <Button variant="secondary">Archive</Button>
      </Toolbar>
      <KeyValueList
        items={[
          { id: "status", term: "Status", description: "Published" },
          { id: "owner", term: "Owner", description: "Ada Lovelace" },
        ]}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "AvatarGroup, Toolbar, and KeyValueList provide compact, semantically labeled supporting data patterns.",
      },
    },
  },
};
