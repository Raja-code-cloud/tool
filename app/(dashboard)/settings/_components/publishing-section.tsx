"use client";

import * as React from "react";

import { Button, Input, Switch } from "@/components/ui";
import { APPROVAL_ROLES, TIMEZONES } from "@/constants/settings";
import { useToast } from "@/hooks/use-toast";
import { settingsService } from "@/lib/services";

import { SelectField } from "./select-field";
import { SettingRow, SettingRows, SettingsSection } from "./settings-section";

const publishingDefaults = settingsService.getPublishingDefaults();

export function PublishingSection(): React.JSX.Element {
  const { toast } = useToast();
  const [timezone, setTimezone] = React.useState<string>(publishingDefaults.defaultTimezone);
  const [approvalRole, setApprovalRole] = React.useState<string>("editor");
  const [dailyLimit, setDailyLimit] = React.useState<string>(publishingDefaults.dailyLimit);
  const [autoQueue, setAutoQueue] = React.useState<boolean>(publishingDefaults.autoQueue);
  const [requireApproval, setRequireApproval] = React.useState<boolean>(
    publishingDefaults.requireApproval,
  );
  const [appendUtm, setAppendUtm] = React.useState<boolean>(publishingDefaults.appendUtm);
  const [retryFailed, setRetryFailed] = React.useState<boolean>(publishingDefaults.retryFailed);

  return (
    <SettingsSection
      id="publishing"
      title="Publishing"
      description="Defaults applied to every scheduled and queued post."
      footer={
        <Button size="compact" onClick={() => toast({ title: "Publishing defaults saved" })}>
          Save defaults
        </Button>
      }
    >
      <SettingRows>
        <SettingRow
          label="Default publishing timezone"
          description="Scheduling times are interpreted in this timezone."
          htmlFor="publishing-timezone"
          control={
            <SelectField
              id="publishing-timezone"
              label="Default publishing timezone"
              hasExternalLabel
              value={timezone}
              options={TIMEZONES}
              onValueChange={setTimezone}
            />
          }
        />
        <SettingRow
          label="Auto-queue approved content"
          description="Approved posts enter the next available publishing slot."
          control={
            <Switch
              checked={autoQueue}
              onCheckedChange={setAutoQueue}
              aria-label="Auto-queue approved content"
            />
          }
        />
        <SettingRow
          label="Require approval before publishing"
          control={
            <Switch
              checked={requireApproval}
              onCheckedChange={setRequireApproval}
              aria-label="Require approval before publishing"
            />
          }
        />
        <SettingRow
          label="Who can approve"
          description="Only these roles can release content to a live channel."
          htmlFor="publishing-approver"
          control={
            <SelectField
              id="publishing-approver"
              label="Who can approve"
              hasExternalLabel
              value={approvalRole}
              options={APPROVAL_ROLES}
              onValueChange={setApprovalRole}
            />
          }
        />
        <SettingRow
          label="Daily publishing limit"
          description="Maximum posts per channel per day. Leave empty for no limit."
          htmlFor="publishing-limit"
          control={
            <Input
              id="publishing-limit"
              type="number"
              min={0}
              max={99}
              inputMode="numeric"
              value={dailyLimit}
              onChange={(event) => setDailyLimit(event.target.value)}
            />
          }
        />
        <SettingRow
          label="Append UTM parameters"
          description="Adds campaign tracking to every outbound link."
          control={
            <Switch
              checked={appendUtm}
              onCheckedChange={setAppendUtm}
              aria-label="Append UTM parameters"
            />
          }
        />
        <SettingRow
          label="Retry failed publishes"
          description="Automatically retry up to three times with backoff."
          control={
            <Switch
              checked={retryFailed}
              onCheckedChange={setRetryFailed}
              aria-label="Retry failed publishes"
            />
          }
        />
      </SettingRows>
    </SettingsSection>
  );
}
