import type { Meta, StoryObj } from "@storybook/react";

import {
  PlatformAvatar,
  PlatformBadge,
  PlatformChip,
  PlatformDots,
  PlatformIcon,
} from "../components/platform";

const platforms = ["linkedin", "facebook", "instagram", "x", "medium", "youtube"] as const;

const meta = {
  title: "Platform/Social Platforms",
  component: PlatformIcon,
  parameters: {
    docs: {
      description: {
        component:
          "Platform identity components share the canonical platform configuration. Visible names or explicit labels prevent icon and color-only identification.",
      },
    },
  },
  args: { platform: "linkedin", label: "LinkedIn" },
  argTypes: { platform: { control: "select", options: platforms } },
} satisfies Meta<typeof PlatformIcon>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Icons: Story = {
  render: () => (
    <div className="flex flex-wrap gap-5">
      {platforms.map((platform) => (
        <PlatformIcon key={platform} platform={platform} label={platform} className="size-8" />
      ))}
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "PlatformIcon renders a known icon or text fallback; pass label when the icon carries meaning.",
      },
    },
  },
};

export const ChipsBadgesAndAvatars: Story = {
  render: () => (
    <div className="grid gap-4">
      <div className="flex flex-wrap gap-2">
        {platforms.map((platform) => (
          <PlatformChip key={platform} platform={platform} showIcon />
        ))}
      </div>
      <div className="flex flex-wrap gap-2">
        {platforms.map((platform) => (
          <PlatformBadge key={platform} platform={platform} />
        ))}
      </div>
      <div className="flex flex-wrap gap-2">
        {platforms.map((platform) => (
          <PlatformAvatar key={platform} platform={platform} />
        ))}
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "PlatformChip, PlatformBadge, and PlatformAvatar provide progressively stronger visual treatments while retaining platform names or fallbacks.",
      },
    },
  },
};

export const Dots: Story = {
  render: () => (
    <div className="grid gap-3">
      <PlatformDots platforms={platforms} />
      <PlatformDots platforms={platforms} size="md" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "PlatformDots offers compact small and medium indicators with a combined accessible label.",
      },
    },
  },
};
