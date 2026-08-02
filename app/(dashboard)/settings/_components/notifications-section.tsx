"use client";

import * as React from "react";

import { Button, Checkbox, Label } from "@/components/ui";
import { NOTIFICATION_PREFERENCES } from "@/constants/settings";
import { useToast } from "@/hooks/use-toast";

import { SettingsSection } from "./settings-section";
import { useSettingsState } from "./use-settings-state";

export function NotificationsSection(): React.JSX.Element {
  const { toast } = useToast();
  const {
    notificationPreferences,
    isLoading,
    isSaving,
    error,
    saveNotificationPreferences,
    setPreference,
  } = useSettingsState();

  async function handleSave(): Promise<void> {
    const saved = await saveNotificationPreferences();
    if (saved) {
      toast({ title: "Notification preferences saved" });
    } else if (error) {
      toast({ title: "Could not save preferences", description: error });
    }
  }

  const rows = NOTIFICATION_PREFERENCES.map((catalog) => ({
    ...catalog,
    email: notificationPreferences?.[catalog.id]?.email ?? catalog.email,
    inApp: notificationPreferences?.[catalog.id]?.inApp ?? catalog.inApp,
  }));

  return (
    <SettingsSection
      id="notifications"
      title="Notifications"
      description="Choose which events reach you, and where."
      footer={
        <Button size="compact" disabled={isSaving || isLoading} onClick={() => void handleSave()}>
          {isSaving ? "Saving…" : "Save preferences"}
        </Button>
      }
    >
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <caption className="sr-only">Notification preferences by channel</caption>
          <thead>
            <tr className="border-b">
              <th
                scope="col"
                className="text-muted-foreground pb-2 text-left text-xs font-semibold"
              >
                Event
              </th>
              <th
                scope="col"
                className="text-muted-foreground w-24 pb-2 text-center text-xs font-semibold"
              >
                Email
              </th>
              <th
                scope="col"
                className="text-muted-foreground w-24 pb-2 text-center text-xs font-semibold"
              >
                In-app
              </th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {rows.map((preference) => (
              <tr key={preference.id}>
                <th scope="row" className="py-3.5 pr-4 text-left font-normal">
                  <span className="block text-sm font-semibold">{preference.label}</span>
                  <span className="text-muted-foreground mt-1 block text-sm">
                    {preference.description}
                  </span>
                </th>
                <td className="py-3.5 text-center">
                  <Label htmlFor={`${preference.id}-email`} className="sr-only">
                    {preference.label} by email
                  </Label>
                  <Checkbox
                    id={`${preference.id}-email`}
                    checked={preference.email}
                    disabled={isLoading}
                    onCheckedChange={(checked) =>
                      setPreference(preference.id, "email", checked === true)
                    }
                    className="mx-auto"
                  />
                </td>
                <td className="py-3.5 text-center">
                  <Label htmlFor={`${preference.id}-inapp`} className="sr-only">
                    {preference.label} in app
                  </Label>
                  <Checkbox
                    id={`${preference.id}-inapp`}
                    checked={preference.inApp}
                    disabled={isLoading}
                    onCheckedChange={(checked) =>
                      setPreference(preference.id, "inApp", checked === true)
                    }
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
