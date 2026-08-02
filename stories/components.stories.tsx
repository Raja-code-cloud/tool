import type { Meta, StoryObj } from "@storybook/react";
import { Check, Copy, Plus, Trash2 } from "lucide-react";

import {
  ActionButton,
  CopyButton,
  DestructiveButton,
  IconButton,
  OutlineButton,
  PrimaryButton,
  SecondaryButton,
} from "../components/buttons";
import {
  AnalyticsCard,
  Card,
  CardHeader,
  ContentCard,
  InteractiveCard,
  MetricCard,
  StatCard,
  UploadCard,
} from "../components/cards";

const meta = {
  title: "Components/Buttons and Cards",
  component: ActionButton,
  parameters: {
    docs: {
      description: {
        component:
          "Application-level button and card compositions. They retain native semantics, keyboard focus, responsive wrapping, and theme tokens.",
      },
    },
  },
  args: { children: "Create item" },
} satisfies Meta<typeof ActionButton>;

export default meta;
type Story = StoryObj<typeof meta>;

export const ButtonCompositions: Story = {
  render: () => (
    <div className="flex flex-wrap gap-3">
      <PrimaryButton>Primary</PrimaryButton>
      <SecondaryButton>Secondary</SecondaryButton>
      <OutlineButton>Outline</OutlineButton>
      <DestructiveButton>Delete</DestructiveButton>
      <ActionButton leadingIcon={<Plus />}>Create</ActionButton>
      <IconButton label="Delete item" icon={<Trash2 />} />
      <CopyButton value="storybook" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "PrimaryButton, SecondaryButton, OutlineButton, DestructiveButton, ActionButton, IconButton, and CopyButton. Icon-only controls always require a meaningful label.",
      },
    },
  },
};

export const CardCompositions: Story = {
  render: () => (
    <div className="tablet:grid-cols-2 desktop:grid-cols-3 grid gap-4">
      <Card>
        <CardHeader
          title="Card and CardHeader"
          description="General content grouping."
          action={<IconButton label="Copy" icon={<Copy />} />}
        />
        <p>Card body content.</p>
      </Card>
      <ContentCard>
        <CardHeader title="ContentCard" />
        <p>Semantic alias for Card.</p>
      </ContentCard>
      <InteractiveCard href="#details" title="InteractiveCard">
        The entire card has one clear link target.
      </InteractiveCard>
      <MetricCard label="Reach" value="124K" trend={<Check />} comparison="+12% this month" />
      <StatCard label="Posts" value="48" comparison="8 scheduled" />
      <AnalyticsCard label="Engagement" value="6.4%" comparison="+0.8 points" />
      <UploadCard>
        <CardHeader title="UploadCard" description="Dashed treatment for upload contexts." />
      </UploadCard>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "Card, CardHeader, ContentCard, InteractiveCard, MetricCard, StatCard, AnalyticsCard, and UploadCard. Responsive grids collapse without changing reading order.",
      },
    },
  },
};
