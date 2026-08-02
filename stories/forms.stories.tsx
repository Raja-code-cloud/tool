import type { Meta, StoryObj } from "@storybook/react";
import * as React from "react";

import {
  CharacterCount,
  FormErrorSummary,
  FormField,
  SearchBar,
  SearchField,
  SearchInput,
} from "../components/forms";
import { SelectField } from "../components/shared/select-field";
import { Input, Textarea } from "../components/ui";

const meta = {
  title: "Forms/Fields",
  component: FormField,
  args: { id: "field", label: "Field label", children: <Input /> },
  parameters: {
    docs: {
      description: {
        component:
          "Labeled form compositions with descriptions, errors, required state, and controlled values. Error text is programmatically associated with its input.",
      },
    },
  },
} satisfies Meta<typeof FormField>;

export default meta;
type Story = StoryObj<typeof meta>;

export const FormFields: Story = {
  render: () => (
    <div className="grid max-w-lg gap-5">
      <FormField id="title" label="Title" isRequired description="Shown publicly.">
        <Input />
      </FormField>
      <FormField id="summary" label="Summary" error="Enter at least 20 characters.">
        <Textarea defaultValue="Too short" />
      </FormField>
      <div className="flex justify-end">
        <CharacterCount current={18} maximum={120} />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "FormField clones one form control to attach ids and ARIA metadata; CharacterCount announces changes and warns near the limit.",
      },
    },
  },
};

export const SearchAliases: Story = {
  render: () => (
    <div className="grid max-w-lg gap-4">
      <SearchField placeholder="Search assets" />
      <SearchInput placeholder="Search campaigns" />
      <SearchBar placeholder="Search posts" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "SearchField, SearchInput, and SearchBar are equivalent semantic aliases; customize their accessible label when context is not obvious.",
      },
    },
  },
};

export const SelectFieldStory: Story = {
  render: function ControlledSelectField() {
    const [value, setValue] = React.useState("draft");
    return (
      <div className="max-w-sm">
        <SelectField
          id="status"
          label="Status"
          description="Controls publication state."
          value={value}
          onValueChange={setValue}
          options={[
            { value: "draft", label: "Draft" },
            { value: "published", label: "Published" },
          ]}
        />
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story:
          "SelectField combines a visible label, optional help text, and the shared Select primitive.",
      },
    },
  },
};

export const ErrorSummary: Story = {
  render: () => (
    <FormErrorSummary
      errors={[
        { id: "title", message: "Enter a title." },
        { id: "summary", message: "Enter a summary." },
      ]}
    />
  ),
  parameters: {
    docs: {
      description: {
        story: "FormErrorSummary uses alert semantics and links each message to its invalid field.",
      },
    },
  },
};
