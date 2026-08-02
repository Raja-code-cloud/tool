"use client";

import * as React from "react";

import { Progress } from "@/components/feedback";
import { Button, Switch } from "@/components/ui";
import { RETENTION_OPTIONS, STORAGE_REGIONS } from "@/constants/settings";
import { settingsService } from "@/lib/services";
import { formatBytes, formatPercent } from "@/lib/utils/formatting";

import { SelectField } from "./select-field";
import { SettingRow, SettingRows, SettingsSection } from "./settings-section";

export function StorageSection(): React.JSX.Element {
  const storageUsage = settingsService.getStorageUsage();
  const [region, setRegion] = React.useState<string>(storageUsage.region);
  const [retention, setRetention] = React.useState<string>("365");
  const [autoArchive, setAutoArchive] = React.useState(true);

  const usedRatio = storageUsage.usedBytes / storageUsage.totalBytes;

  return (
    <SettingsSection
      id="storage"
      title="Storage"
      description="Where your media lives and how long it is kept."
      action={
        <Button variant="secondary" size="compact">
          Manage files
        </Button>
      }
    >
      <div className="border-b pb-5">
        <Progress value={Math.round(usedRatio * 100)} label="Storage used" />
        <p className="text-muted-foreground mt-2 text-sm">
          {formatBytes(storageUsage.usedBytes)} of {formatBytes(storageUsage.totalBytes)} used (
          {formatPercent(usedRatio)}).
        </p>

        <dl className="tablet:grid-cols-2 desktop:grid-cols-4 mt-4 grid gap-3">
          {storageUsage.breakdown.map((entry) => (
            <div key={entry.id} className="rounded-lg border p-3">
              <dt className="text-muted-foreground text-xs font-semibold">{entry.label}</dt>
              <dd className="mt-1 text-sm font-semibold tabular-nums">
                {formatBytes(entry.bytes)}
              </dd>
            </div>
          ))}
        </dl>
      </div>

      <SettingRows>
        <SettingRow
          label="Storage region"
          description="Media is stored at rest in this region. Changing it triggers a migration."
          htmlFor="storage-region"
          control={
            <SelectField
              id="storage-region"
              label="Storage region"
              hasExternalLabel
              value={region}
              options={STORAGE_REGIONS}
              onValueChange={setRegion}
            />
          }
        />
        <SettingRow
          label="Retention policy"
          description="How long archived assets are retained before deletion."
          htmlFor="storage-retention"
          control={
            <SelectField
              id="storage-retention"
              label="Retention policy"
              hasExternalLabel
              value={retention}
              options={RETENTION_OPTIONS}
              onValueChange={setRetention}
            />
          }
        />
        <SettingRow
          label="Auto-archive published media"
          description="Move assets to cold storage 30 days after publishing."
          control={
            <Switch
              checked={autoArchive}
              onCheckedChange={setAutoArchive}
              aria-label="Auto-archive published media"
            />
          }
        />
      </SettingRows>
    </SettingsSection>
  );
}
