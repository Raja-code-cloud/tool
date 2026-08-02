import type { Meta, StoryObj } from "@storybook/react";
import * as React from "react";

import {
  Avatar,
  Badge,
  Button,
  Checkbox,
  Input,
  Label,
  RadioGroup,
  RadioGroupItem,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Separator,
  Switch,
  Textarea,
} from "../components/ui";

const meta = {
  title: "Foundations/Primitives",
  component: Button,
  parameters: {
    docs: {
      description: {
        component:
          "Core form and display primitives. All controls expose native or Radix props, visible focus, disabled states, and semantic labels. Use these building blocks before creating a specialized component.",
      },
    },
  },
  args: { children: "Continue" },
  argTypes: {
    variant: {
      control: "select",
      options: ["primary", "secondary", "outline", "ghost", "destructive", "icon"],
    },
    size: { control: "select", options: ["compact", "default", "prominent"] },
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Buttons: Story = {
  render: (args) => (
    <div className="flex flex-wrap gap-3">
      {(["primary", "secondary", "outline", "ghost", "destructive"] as const).map((variant) => (
        <Button {...args} key={variant} variant={variant}>
          {variant}
        </Button>
      ))}
      <Button {...args} isLoading>
        Saving
      </Button>
      <Button {...args} disabled>
        Disabled
      </Button>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "Button variants, loading, and disabled states. Loading announces busy state and prevents duplicate activation.",
      },
    },
  },
};

export const TextInputs: Story = {
  render: () => (
    <div className="grid max-w-md gap-5">
      <div className="grid gap-2">
        <Label htmlFor="name">Name</Label>
        <Input id="name" placeholder="Ada Lovelace" />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="bio">Biography</Label>
        <Textarea id="bio" placeholder="Write a short biography" />
      </div>
      <Input aria-label="Invalid example" aria-invalid defaultValue="Invalid value" />
      <Input aria-label="Disabled example" disabled value="Disabled" readOnly />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "Input, Textarea, and Label usage with explicit labels, validation, and disabled states.",
      },
    },
  },
};

export const ChoiceControls: Story = {
  render: function ChoiceControlsStory() {
    const [enabled, setEnabled] = React.useState(true);
    const [choice, setChoice] = React.useState("weekly");
    return (
      <div className="grid gap-5">
        <label className="flex items-center gap-2">
          <Checkbox defaultChecked /> Email updates
        </label>
        <label className="flex items-center gap-2">
          <Switch checked={enabled} onCheckedChange={setEnabled} /> Publishing enabled
        </label>
        <RadioGroup
          aria-label="Digest frequency"
          value={choice}
          onValueChange={setChoice}
          className="grid gap-2"
        >
          {["daily", "weekly", "monthly"].map((value) => (
            <label className="flex items-center gap-2" key={value}>
              <RadioGroupItem value={value} />
              {value}
            </label>
          ))}
        </RadioGroup>
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story:
          "Checkbox, Switch, RadioGroup, and RadioGroupItem support keyboard interaction and controlled or uncontrolled state.",
      },
    },
  },
};

export const SelectPrimitive: Story = {
  render: () => (
    <Select defaultValue="draft">
      <SelectTrigger className="max-w-xs" aria-label="Status">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="draft">Draft</SelectItem>
        <SelectItem value="scheduled">Scheduled</SelectItem>
        <SelectItem value="published">Published</SelectItem>
      </SelectContent>
    </Select>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "Select, SelectTrigger, SelectValue, SelectContent, and SelectItem compose an accessible listbox.",
      },
    },
  },
};

export const DisplayPrimitives: Story = {
  render: () => (
    <div className="grid gap-5">
      <div className="flex items-center gap-3">
        <Avatar alt="Ada Lovelace" fallback="AL" /> <Avatar alt="Grace Hopper" size="lg" />
      </div>
      <div className="flex flex-wrap gap-2">
        {(["neutral", "info", "success", "warning", "danger"] as const).map((variant) => (
          <Badge key={variant} variant={variant}>
            {variant}
          </Badge>
        ))}
      </div>
      <Separator />
      <div className="flex h-8 items-center gap-3">
        Left <Separator orientation="vertical" /> Right
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "Avatar provides text fallback; Badge communicates labeled status; Separator is decorative structure.",
      },
    },
  },
};
