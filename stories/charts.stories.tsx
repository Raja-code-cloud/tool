import type { Meta, StoryObj } from "@storybook/react";

import {
  BarChart,
  ChartContainer,
  ChartDataTable,
  ChartFrame,
  ChartLegend,
  KPIWidget,
} from "../components/charts";

const data = [
  { label: "LinkedIn", value: 72 },
  { label: "Instagram", value: 54 },
  { label: "YouTube", value: 31 },
];

const meta = {
  title: "Charts/Accessible Charts",
  component: ChartFrame,
  parameters: {
    docs: {
      description: {
        component:
          "Chart compositions pair a visual summary with text, legends, and optional tabular data. Never use color as the only means of identifying a series.",
      },
    },
  },
  args: { title: "Channel reach", summary: "LinkedIn leads with 72 thousand impressions." },
} satisfies Meta<typeof ChartFrame>;

export default meta;
type Story = StoryObj<typeof meta>;

export const BarChartWithLegend: Story = {
  render: (args) => (
    <ChartFrame
      {...args}
      period="Last 30 days"
      units="Thousands"
      legend={<ChartLegend items={[{ label: "Impressions", colorClassName: "bg-primary" }]} />}
    >
      <BarChart data={data} valueFormatter={(value) => `${value}K`} />
      <ChartDataTable
        caption="Channel reach data"
        data={data}
        valueHeading="Impressions"
        valueFormatter={(value) => `${value}K`}
      />
    </ChartFrame>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "ChartFrame, ChartLegend, BarChart, and ChartDataTable create a responsive visual with an equivalent accessible table.",
      },
    },
  },
};

export const ContainerAliasAndKPI: Story = {
  render: () => (
    <div className="tablet:grid-cols-2 grid gap-4">
      <ChartContainer title="Publishing volume" summary="Publishing volume rose this week.">
        <BarChart data={data} />
      </ChartContainer>
      <KPIWidget label="Engagement rate" value="6.4%" detail="+0.8 points versus prior period" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "ChartContainer is the semantic alias for ChartFrame; KPIWidget displays one key metric and supporting context.",
      },
    },
  },
};
