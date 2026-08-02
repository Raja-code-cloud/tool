"use client";

import { ChevronDown, ChevronUp, Settings2 } from "lucide-react";

import { Card } from "@/components/cards";
import { Button, Checkbox, Label, RadioGroup, RadioGroupItem } from "@/components/ui";
import { AI_STUDIO_AUDIENCES, AI_STUDIO_LENGTHS, AI_STUDIO_TONES } from "@/constants/ai-studio";
import { cn } from "@/lib/utils/cn";

import type { AiStudioSettings } from "./types";

export type AiSettingsPanelProps = {
  settings: AiStudioSettings;
  providers: readonly import("@/lib/domain/ai-studio-generation").AiStudioProviderOption[];
  onChange: (patch: Partial<AiStudioSettings>) => void;
  isOpen: boolean;
  onToggle: () => void;
};

export function AiSettingsPanel({
  settings,
  providers,
  onChange,
  isOpen,
  onToggle,
}: AiSettingsPanelProps): React.JSX.Element {
  return (
    <Card className="overflow-hidden p-0">
      <button
        type="button"
        className="hover:bg-muted/40 flex w-full items-center justify-between gap-3 p-4 text-left"
        aria-expanded={isOpen}
        onClick={onToggle}
      >
        <span className="flex items-center gap-2 text-sm font-semibold">
          <Settings2 className="size-4" aria-hidden="true" />
          AI settings
        </span>
        {isOpen ? (
          <ChevronUp className="size-4" aria-hidden="true" />
        ) : (
          <ChevronDown className="size-4" aria-hidden="true" />
        )}
      </button>
      <div className={cn("grid gap-4 border-t px-4 pb-4", !isOpen && "hidden")}>
        {providers.length > 0 && (
          <section aria-labelledby="provider-settings">
            <h3
              id="provider-settings"
              className="text-muted-foreground text-xs font-semibold tracking-wide uppercase"
            >
              AI provider
            </h3>
            <RadioGroup
              value={settings.modelId ?? providers[0]?.modelId ?? ""}
              onValueChange={(value) => onChange({ modelId: value })}
              className="mt-2 grid gap-1.5"
            >
              {providers.map((provider) => (
                <label
                  key={provider.id}
                  className="flex items-center gap-2 rounded-md border px-2.5 py-2 text-sm"
                >
                  <RadioGroupItem value={provider.modelId} id={`ai-provider-${provider.id}`} />
                  <span>
                    {provider.name}
                    {provider.status !== "enabled" ? ` (${provider.status})` : ""}
                  </span>
                </label>
              ))}
            </RadioGroup>
          </section>
        )}
        <section aria-labelledby="tone-settings">
          <h3
            id="tone-settings"
            className="text-muted-foreground text-xs font-semibold tracking-wide uppercase"
          >
            Tone
          </h3>
          <RadioGroup
            value={settings.tone}
            onValueChange={(value) => onChange({ tone: value as AiStudioSettings["tone"] })}
            className="mt-2 grid gap-1.5 sm:grid-cols-2"
          >
            {AI_STUDIO_TONES.map((tone) => (
              <label
                key={tone.value}
                className="flex items-center gap-2 rounded-md border px-2.5 py-2 text-sm"
              >
                <RadioGroupItem value={tone.value} id={`ai-tone-${tone.value}`} />
                <span>{tone.label}</span>
              </label>
            ))}
          </RadioGroup>
        </section>
        <section aria-labelledby="length-settings">
          <h3
            id="length-settings"
            className="text-muted-foreground text-xs font-semibold tracking-wide uppercase"
          >
            Length
          </h3>
          <RadioGroup
            value={settings.length}
            onValueChange={(value) => onChange({ length: value as AiStudioSettings["length"] })}
            className="mt-2 flex flex-wrap gap-2"
          >
            {AI_STUDIO_LENGTHS.map((item) => (
              <label
                key={item.value}
                className="flex items-center gap-2 rounded-md border px-2.5 py-2 text-sm"
              >
                <RadioGroupItem value={item.value} id={`ai-length-${item.value}`} />
                <span>{item.label}</span>
              </label>
            ))}
          </RadioGroup>
        </section>
        <section aria-labelledby="audience-settings">
          <h3
            id="audience-settings"
            className="text-muted-foreground text-xs font-semibold tracking-wide uppercase"
          >
            Audience
          </h3>
          <RadioGroup
            value={settings.audience}
            onValueChange={(value) => onChange({ audience: value as AiStudioSettings["audience"] })}
            className="mt-2 grid gap-1.5 sm:grid-cols-2"
          >
            {AI_STUDIO_AUDIENCES.map((item) => (
              <label
                key={item.value}
                className="flex items-center gap-2 rounded-md border px-2.5 py-2 text-sm"
              >
                <RadioGroupItem value={item.value} id={`ai-audience-${item.value}`} />
                <span>{item.label}</span>
              </label>
            ))}
          </RadioGroup>
        </section>
        <section className="grid gap-2 sm:grid-cols-2">
          {(
            [
              ["generateHashtags", "Hashtags"],
              ["generateCta", "Call to action"],
              ["generateSeo", "SEO"],
              ["emojiOptimization", "Emoji optimization"],
              ["threadMode", "Thread mode"],
            ] as const
          ).map(([key, label]) => (
            <div key={key} className="flex items-center gap-2 rounded-md border px-2.5 py-2">
              <Checkbox
                id={`ai-${key}`}
                checked={settings[key]}
                onCheckedChange={(checked) => onChange({ [key]: checked === true })}
              />
              <Label htmlFor={`ai-${key}`}>{label}</Label>
            </div>
          ))}
        </section>
        <Button
          type="button"
          variant="ghost"
          size="compact"
          onClick={onToggle}
          className="justify-self-start"
        >
          Collapse settings
        </Button>
      </div>
    </Card>
  );
}
