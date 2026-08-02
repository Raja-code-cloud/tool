"use client";

import * as React from "react";
import { Monitor, Moon, Sun } from "lucide-react";

import { useTheme, type Theme } from "@/components/theme/theme-provider";
import { Label, RadioGroup, RadioGroupItem, Switch } from "@/components/ui";
import { cn } from "@/lib/utils/cn";
import { DENSITY_OPTIONS } from "@/constants/settings";
import { SettingRow, SettingRows, SettingsSection } from "./settings-section";

const THEME_OPTIONS: readonly { value: Theme; label: string; icon: typeof Sun }[] = [
  { value: "light", label: "Light", icon: Sun },
  { value: "dark", label: "Dark", icon: Moon },
  { value: "system", label: "System", icon: Monitor },
];

export function AppearanceSection(): React.JSX.Element {
  const { theme, setTheme } = useTheme();
  const [density, setDensity] = React.useState<string>(DENSITY_OPTIONS[0].value);
  const [reduceMotion, setReduceMotion] = React.useState(false);

  return (
    <SettingsSection id="appearance" title="Appearance" description="Theme and layout preferences for this browser.">
      <fieldset className="border-b pb-5">
        <legend className="text-sm font-semibold">Theme</legend>
        <p className="mt-1 text-sm text-muted-foreground">Dark is the default. Your choice is saved to this device.</p>
        <RadioGroup
          value={theme}
          onValueChange={(next) => setTheme(next as Theme)}
          className="mt-4 grid gap-3 tablet:grid-cols-3"
        >
          {THEME_OPTIONS.map((option) => (
            <Label
              key={option.value}
              htmlFor={`theme-${option.value}`}
              className={cn(
                "flex cursor-pointer items-center gap-3 rounded-lg border p-3 text-sm transition-colors hover:bg-accent/40",
                theme === option.value && "border-primary bg-accent/30",
              )}
            >
              <RadioGroupItem id={`theme-${option.value}`} value={option.value} />
              <option.icon className="size-4" aria-hidden="true" />
              <span className="font-semibold">{option.label}</span>
            </Label>
          ))}
        </RadioGroup>
      </fieldset>

      <SettingRows>
        <SettingRow
          label="Interface density"
          description="Controls row height across tables and lists."
          control={
            <RadioGroup value={density} onValueChange={setDensity} className="grid gap-2">
              {DENSITY_OPTIONS.map((option) => (
                <Label key={option.value} htmlFor={`density-${option.value}`} className="flex cursor-pointer items-center gap-2 text-sm font-normal">
                  <RadioGroupItem id={`density-${option.value}`} value={option.value} />
                  {option.label}
                </Label>
              ))}
            </RadioGroup>
          }
        />
        <SettingRow
          label="Reduce motion"
          description="Minimise transitions and animated chart transforms."
          control={
            <Switch
              checked={reduceMotion}
              onCheckedChange={setReduceMotion}
              aria-label="Reduce motion"
              className="tablet:ml-auto tablet:block"
            />
          }
        />
      </SettingRows>
    </SettingsSection>
  );
}
