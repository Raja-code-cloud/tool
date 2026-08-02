"use client";

import { Card, CardHeader } from "@/components/cards";
import { FormField } from "@/components/forms";
import { SelectField } from "@/components/shared/select-field";
import { Input, Textarea } from "@/components/ui";
import { CONTENT_SERIES, PROJECT_CATEGORIES } from "@/constants/upload-wizard";
import { INPUT_LIMITS } from "@/lib/security";

import type { WizardFormState } from "../wizard-types";

export type StepProjectInfoProps = {
  form: WizardFormState;
  errors: Readonly<Record<string, string>>;
  onChange: (patch: Partial<WizardFormState>) => void;
};

export function StepProjectInfo({
  form,
  errors,
  onChange,
}: StepProjectInfoProps): React.JSX.Element {
  return (
    <Card>
      <CardHeader
        title="Project information"
        description="Tell us about the publishing project you are creating."
      />
      <div className="tablet:grid-cols-2 grid gap-5">
        <FormField
          id="project-name"
          label="Project name"
          isRequired
          {...(errors.projectName ? { error: errors.projectName } : {})}
        >
          <Input
            value={form.projectName}
            maxLength={INPUT_LIMITS.projectName}
            placeholder="e.g. Azure landing zone launch"
            onChange={(event) => onChange({ projectName: event.target.value })}
          />
        </FormField>
        <FormField
          id="project-category"
          label="Category"
          isRequired
          {...(errors.category ? { error: errors.category } : {})}
        >
          <SelectField
            id="project-category"
            label="Category"
            hasExternalLabel
            value={form.category}
            options={PROJECT_CATEGORIES}
            onValueChange={(value) => onChange({ category: value })}
          />
        </FormField>
        <FormField
          id="project-description"
          label="Description"
          className="tablet:col-span-2"
          description="Optional summary for your team."
        >
          <Textarea
            value={form.description}
            rows={4}
            maxLength={INPUT_LIMITS.description}
            placeholder="What is this campaign about?"
            onChange={(event) => onChange({ description: event.target.value })}
          />
        </FormField>
        <FormField
          id="project-tags"
          label="Tags"
          description="Comma-separated tags for search and filtering."
        >
          <Input
            value={form.tags}
            maxLength={INPUT_LIMITS.tags}
            placeholder="cloud, azure, devops"
            onChange={(event) => onChange({ tags: event.target.value })}
          />
        </FormField>
        <FormField id="content-series" label="Content series">
          <SelectField
            id="content-series"
            label="Content series"
            hasExternalLabel
            value={form.contentSeries}
            options={CONTENT_SERIES}
            onValueChange={(value) => onChange({ contentSeries: value })}
          />
        </FormField>
        <FormField id="publish-date" label="Estimated publish date" className="tablet:col-span-2">
          <Input
            type="date"
            value={form.publishDate}
            onChange={(event) => onChange({ publishDate: event.target.value })}
          />
        </FormField>
      </div>
    </Card>
  );
}
