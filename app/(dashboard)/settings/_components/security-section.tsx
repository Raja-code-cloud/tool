"use client";

import { ShieldCheck } from "lucide-react";
import * as React from "react";

import { ConfirmationDialog } from "@/components/dialogs";
import { Badge, Button, Switch } from "@/components/ui";
import { useToast } from "@/hooks/use-toast";
import { settingsService } from "@/lib/services";
import { formatDate } from "@/lib/utils/formatting";

import { SettingRow, SettingRows, SettingsSection } from "./settings-section";

export function SecuritySection(): React.JSX.Element {
  const { toast } = useToast();
  const [twoFactor, setTwoFactor] = React.useState(true);
  const [ssoOnly, setSsoOnly] = React.useState(false);
  const [sessions, setSessions] = React.useState<
    readonly import("@/lib/domain/settings").SessionRecord[]
  >([]);

  React.useEffect(() => {
    void settingsService.listActiveSessions().then(setSessions);
  }, []);

  function revokeOthers(): void {
    setSessions((current) => current.filter((session) => session.isCurrent));
    toast({ title: "Other sessions signed out" });
  }

  const otherSessionCount = sessions.filter((session) => !session.isCurrent).length;

  return (
    <SettingsSection
      id="security"
      title="Security"
      description="Protect your account and review where it is signed in."
    >
      <SettingRows>
        <SettingRow
          label="Two-factor authentication"
          description="Require a one-time code from your authenticator app at sign-in."
          control={
            <div className="flex items-center gap-2">
              {twoFactor && (
                <Badge variant="success">
                  <ShieldCheck className="size-3" aria-hidden="true" />
                  On
                </Badge>
              )}
              <Switch
                checked={twoFactor}
                onCheckedChange={setTwoFactor}
                aria-label="Two-factor authentication"
              />
            </div>
          }
        />
        <SettingRow
          label="Enforce single sign-on"
          description="Members must authenticate through your identity provider."
          control={
            <Switch
              checked={ssoOnly}
              onCheckedChange={setSsoOnly}
              aria-label="Enforce single sign-on"
            />
          }
        />
        <SettingRow
          label="Password"
          description="Last changed 3 months ago."
          control={
            <Button variant="secondary" size="compact">
              Change password
            </Button>
          }
        />
      </SettingRows>

      <div className="mt-5 border-t pt-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h3 className="text-sm font-semibold">Active sessions</h3>
          {otherSessionCount > 0 && (
            <ConfirmationDialog
              trigger={
                <Button variant="secondary" size="compact">
                  Sign out other sessions
                </Button>
              }
              title="Sign out other sessions?"
              description={`This immediately ends ${otherSessionCount} other ${otherSessionCount === 1 ? "session" : "sessions"}. You will stay signed in on this device.`}
              confirmLabel="Sign out others"
              onConfirm={revokeOthers}
            />
          )}
        </div>

        <ul className="mt-3 divide-y rounded-lg border">
          {sessions.map((session) => (
            <li
              key={session.id}
              className="flex flex-wrap items-center justify-between gap-2 px-4 py-3"
            >
              <div className="min-w-0">
                <p className="flex items-center gap-2 text-sm font-medium">
                  {session.device}
                  {session.isCurrent && <Badge variant="info">This device</Badge>}
                </p>
                <p className="text-muted-foreground mt-0.5 text-sm">
                  {session.location} · Last active {formatDate(session.lastActive)}
                </p>
              </div>
              {!session.isCurrent && (
                <Button
                  variant="ghost"
                  size="compact"
                  onClick={() =>
                    setSessions((current) => current.filter((entry) => entry.id !== session.id))
                  }
                >
                  Revoke
                </Button>
              )}
            </li>
          ))}
        </ul>
      </div>
    </SettingsSection>
  );
}
