"use client";

import { useState } from "react";

import { PrimaryButton, SecondaryButton } from "@/components/buttons";
import { Dialog, DialogContent } from "@/components/dialogs";
import { FormField } from "@/components/forms";
import {
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui";
import { SCHEDULER_PLATFORMS, SCHEDULER_TIMEZONES } from "@/lib/config/scheduler";

import type { QuickScheduleForm } from "./types";

export type QuickScheduleDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaults: QuickScheduleForm;
  onSubmit: (form: QuickScheduleForm) => void;
};

export function QuickScheduleDialog({
  open,
  onOpenChange,
  defaults,
  onSubmit,
}: QuickScheduleDialogProps): React.JSX.Element {
  const [form, setForm] = useState<QuickScheduleForm>(defaults);

  const handleSubmit = (): void => {
    if (!form.title.trim()) return;
    onSubmit(form);
    setForm(defaults);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        title="Create schedule"
        description="Quickly add a post to the publishing queue."
      >
        <div className="grid gap-4">
          <FormField id="qs-title" label="Content title" isRequired>
            <Input
              value={form.title}
              placeholder="e.g. Azure Networking Deep Dive"
              onChange={(event) => setForm((prev) => ({ ...prev, title: event.target.value }))}
            />
          </FormField>
          <FormField id="qs-platform" label="Platform">
            <Select
              value={form.platform}
              onValueChange={(value) => setForm((prev) => ({ ...prev, platform: value }))}
            >
              <SelectTrigger id="qs-platform">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {SCHEDULER_PLATFORMS.map((platform) => (
                  <SelectItem key={platform.id} value={platform.id}>
                    {platform.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </FormField>
          <div className="grid gap-4 sm:grid-cols-2">
            <FormField id="qs-date" label="Date">
              <Input
                type="date"
                value={form.date}
                onChange={(event) => setForm((prev) => ({ ...prev, date: event.target.value }))}
              />
            </FormField>
            <FormField id="qs-time" label="Time">
              <Input
                type="time"
                value={form.time}
                onChange={(event) => setForm((prev) => ({ ...prev, time: event.target.value }))}
              />
            </FormField>
          </div>
          <FormField id="qs-timezone" label="Timezone">
            <Select
              value={form.timezone}
              onValueChange={(value) => setForm((prev) => ({ ...prev, timezone: value }))}
            >
              <SelectTrigger id="qs-timezone">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {SCHEDULER_TIMEZONES.map((tz) => (
                  <SelectItem key={tz.value} value={tz.value}>
                    {tz.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </FormField>
          <FormField id="qs-priority" label="Priority">
            <Select
              value={form.priority}
              onValueChange={(value) =>
                setForm((prev) => ({ ...prev, priority: value as QuickScheduleForm["priority"] }))
              }
            >
              <SelectTrigger id="qs-priority">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="normal">Normal</SelectItem>
                <SelectItem value="high">High</SelectItem>
              </SelectContent>
            </Select>
          </FormField>
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <SecondaryButton type="button" onClick={() => onOpenChange(false)}>
              Cancel
            </SecondaryButton>
            <PrimaryButton type="button" onClick={handleSubmit} disabled={!form.title.trim()}>
              Create schedule
            </PrimaryButton>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
