"use client";

import { Plus } from "lucide-react";
import * as React from "react";

import { StatusBadge } from "@/components/feedback";
import { Badge, Button } from "@/components/ui";
import type { AiProviderStatus } from "@/lib/domain/settings";
import { settingsService } from "@/lib/services";
import { formatNumber } from "@/lib/utils/formatting";

import { SettingsSection } from "./settings-section";

const aiProviders = settingsService.listAiProviders();

const STATUS_META: Record<
  AiProviderStatus,
  { label: string; variant: "success" | "neutral" | "danger" }
> = {
  connected: { label: "Connected", variant: "success" },
  disconnected: { label: "Not connected", variant: "neutral" },
  error: { label: "Action required", variant: "danger" },
};

export function AiProvidersSection(): React.JSX.Element {
  const [defaultProvider, setDefaultProvider] = React.useState<string>(
    aiProviders.find((provider) => provider.isDefault)?.id ?? "",
  );

  return (
    <SettingsSection
      id="ai-providers"
      title="AI Providers"
      description="Model providers available to AI Studio and automated generation."
      action={
        <Button variant="secondary" size="compact">
          <Plus className="size-4" aria-hidden="true" />
          Add provider
        </Button>
      }
    >
      <ul className="grid gap-3">
        {aiProviders.map((provider) => {
          const status = STATUS_META[provider.status];
          const isDefault = provider.id === defaultProvider;

          return (
            <li
              key={provider.id}
              className="desktop:flex-row desktop:items-center desktop:justify-between flex flex-col gap-3 rounded-lg border p-4"
            >
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-sm font-semibold">{provider.name}</h3>
                  <StatusBadge variant={status.variant}>{status.label}</StatusBadge>
                  {isDefault && <Badge variant="info">Default</Badge>}
                </div>
                <p className="text-muted-foreground mt-1 text-sm">
                  {provider.model}
                  {provider.monthlyTokens > 0 &&
                    ` · ${formatNumber(provider.monthlyTokens)} tokens this month`}
                </p>
              </div>

              <div className="flex shrink-0 flex-wrap gap-2">
                {provider.status === "connected" && !isDefault && (
                  <Button
                    variant="secondary"
                    size="compact"
                    onClick={() => setDefaultProvider(provider.id)}
                  >
                    Make default
                  </Button>
                )}
                <Button
                  variant={provider.status === "disconnected" ? "primary" : "outline"}
                  size="compact"
                >
                  {provider.status === "disconnected" ? "Connect" : "Configure"}
                </Button>
              </div>
            </li>
          );
        })}
      </ul>
    </SettingsSection>
  );
}
