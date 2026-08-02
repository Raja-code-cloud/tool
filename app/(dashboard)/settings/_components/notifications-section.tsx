"use client";

import * as React from "react";

import { Button, Checkbox, Label } from "@/components/ui";
import { useToast } from "@/hooks/use-toast";
import { NOTIFICATION_PREFERENCES, type NotificationChannelId } from "@/constants/settings";
import { SettingsSection } from "./settings-section";

type ChannelState = Record<NotificationChannelId, { email: boolean; inApp: boolean }>;

function buildInitialState(): ChannelState {
  return NOTIFICATION_PREFERENCES.reduce<ChannelState>((accumulator, preference) => {
    accumulator[preference.id] = { email: preference.email, inApp: preference.inApp };
    return accumulator;
  }, {} as ChannelState);
}

export function NotificationsSection(): React.JSX.Element {
  const { toast } = useToast();
  const [state, setState] = React.useState<ChannelState>(buildInitialState);

  function toggle(id: NotificationChannelId, channel: "email" | "inApp", checked: boolean): void {
    setState((current) => ({ ...current, [id]: { ...current[id], [channel]: checked } }));
  }

  return (
    <SettingsSection
      id="notifications"
      title="Notifications"
      description="Choose which events reach you, and where."
      footer={<Button size="compact" onClick={() => toast({ title: "Notification preferences saved" })}>Save preferences</Button>}
    >
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <caption className="sr-only">Notification preferences by channel</caption>
          <thead>
            <tr className="border-b">
              <th scope="col" className="pb-2 text-left text-xs font-semibold text-muted-foreground">Event</th>
              <th scope="col" className="w-24 pb-2 text-center text-xs font-semibold text-muted-foreground">Email</th>
              <th scope="col" className="w-24 pb-2 text-center text-xs font-semibold text-muted-foreground">In-app</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {NOTIFICATION_PREFERENCES.map((preference) => (
              <tr key={preference.id}>
                <th scope="row" className="py-3.5 pr-4 text-left font-normal">
                  <span className="block text-sm font-semibold">{preference.label}</span>
                  <span className="mt-1 block text-sm text-muted-foreground">{preference.description}</span>
                </th>
                <td className="py-3.5 text-center">
                  <Label htmlFor={`${preference.id}-email`} className="sr-only">{preference.label} by email</Label>
                  <Checkbox
                    id={`${preference.id}-email`}
                    checked={state[preference.id].email}
                    onCheckedChange={(checked) => toggle(preference.id, "email", checked === true)}
                    className="mx-auto"
                  />
                </td>
                <td className="py-3.5 text-center">
                  <Label htmlFor={`${preference.id}-inapp`} className="sr-only">{preference.label} in app</Label>
                  <Checkbox
                    id={`${preference.id}-inapp`}
                    checked={state[preference.id].inApp}
                    onCheckedChange={(checked) => toggle(preference.id, "inApp", checked === true)}
                    className="mx-auto"
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </SettingsSection>
  );
}
