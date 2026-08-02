"use client";

import { Card, CardHeader } from "@/components/cards";
import { Alert } from "@/components/feedback";
import { Badge, Checkbox, Label, RadioGroup, RadioGroupItem } from "@/components/ui";
import { AI_LENGTHS, AI_PLATFORMS, AI_TONES } from "@/constants/upload-wizard";
import { cn } from "@/lib/utils/cn";

import type { WizardFormState } from "../wizard-types";

export type StepAiSettingsProps = {
  form: WizardFormState;
  errors: Readonly<Record<string, string>>;
  onChange: (patch: Partial<WizardFormState>) => void;
};

export function StepAiSettings({ form, errors, onChange }: StepAiSettingsProps): React.JSX.Element {
  const togglePlatform = (platformId: string) => {
    const exists = form.platforms.includes(platformId);
    onChange({
      platforms: exists
        ? form.platforms.filter((id) => id !== platformId)
        : [...form.platforms, platformId],
    });
  };

  return (
    <Card>
      <CardHeader
        title="AI generation settings"
        description="Choose platforms, tone, and length for AI-generated social variants."
      />
      <div className="grid gap-6">
        <section aria-labelledby="platforms-heading">
          <h3 id="platforms-heading" className="text-sm font-semibold">
            Platforms
          </h3>
          <p className="text-muted-foreground mt-1 text-xs">
            Select where you want AI to generate content.
          </p>
          <div className="mt-3 grid gap-2 sm:grid-cols-2">
            {AI_PLATFORMS.map((platform) => {
              const selected = form.platforms.includes(platform.id);
              return (
                <button
                  key={platform.id}
                  type="button"
                  aria-pressed={selected}
                  onClick={() => togglePlatform(platform.id)}
                  className={cn(
                    "flex items-center justify-between rounded-lg border px-3 py-2.5 text-left text-sm transition-colors",
                    selected ? "border-primary bg-accent" : "hover:bg-muted/60",
                  )}
                >
                  {platform.label}
                  {selected && <Badge variant="success">Selected</Badge>}
                </button>
              );
            })}
          </div>
          {errors.platforms && (
            <p role="alert" className="text-destructive mt-2 text-xs">
              {errors.platforms}
            </p>
          )}
        </section>

        <section aria-labelledby="tone-heading">
          <h3 id="tone-heading" className="text-sm font-semibold">
            Tone
          </h3>
          <RadioGroup
            value={form.tone}
            onValueChange={(value) => onChange({ tone: value })}
            className="mt-3 grid gap-2 sm:grid-cols-2"
          >
            {AI_TONES.map((tone) => (
              <label
                key={tone.value}
                className="hover:bg-muted/60 flex items-center gap-2 rounded-lg border px-3 py-2.5 text-sm"
              >
                <RadioGroupItem value={tone.value} id={`tone-${tone.value}`} />
                <span>{tone.label}</span>
              </label>
            ))}
          </RadioGroup>
        </section>

        <section aria-labelledby="length-heading">
          <h3 id="length-heading" className="text-sm font-semibold">
            Length
          </h3>
          <RadioGroup
            value={form.length}
            onValueChange={(value) => onChange({ length: value })}
            className="mt-3 flex flex-wrap gap-2"
          >
            {AI_LENGTHS.map((item) => (
              <label
                key={item.value}
                className="hover:bg-muted/60 flex items-center gap-2 rounded-lg border px-3 py-2.5 text-sm"
              >
                <RadioGroupItem value={item.value} id={`length-${item.value}`} />
                <span>{item.label}</span>
              </label>
            ))}
          </RadioGroup>
        </section>

        <section aria-labelledby="options-heading" className="grid gap-3 sm:grid-cols-3">
          <h3 id="options-heading" className="sr-only">
            Generation options
          </h3>
          <div className="flex items-center gap-2 rounded-lg border px-3 py-2.5">
            <Checkbox
              id="generate-hashtags"
              checked={form.generateHashtags}
              onCheckedChange={(checked) => onChange({ generateHashtags: checked === true })}
            />
            <Label htmlFor="generate-hashtags">Generate hashtags</Label>
          </div>
          <div className="flex items-center gap-2 rounded-lg border px-3 py-2.5">
            <Checkbox
              id="generate-cta"
              checked={form.generateCta}
              onCheckedChange={(checked) => onChange({ generateCta: checked === true })}
            />
            <Label htmlFor="generate-cta">Generate CTA</Label>
          </div>
          <div className="flex items-center gap-2 rounded-lg border px-3 py-2.5">
            <Checkbox
              id="generate-seo"
              checked={form.generateSeo}
              onCheckedChange={(checked) => onChange({ generateSeo: checked === true })}
            />
            <Label htmlFor="generate-seo">Generate SEO</Label>
          </div>
        </section>
      </div>
      {(errors.tone || errors.length) && (
        <Alert variant="danger" title="Complete AI settings" className="mt-4">
          {errors.tone ?? errors.length}
        </Alert>
      )}
    </Card>
  );
}
