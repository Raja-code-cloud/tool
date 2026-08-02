"use client";

import * as React from "react";

import { ConfirmationDialog } from "@/components/dialogs";
import { Button } from "@/components/ui";
import { useToast } from "@/hooks/use-toast";

import { SettingsSection } from "./settings-section";

type DangerAction = {
  readonly id: string;
  readonly title: string;
  readonly description: string;
  readonly buttonLabel: string;
  readonly dialogTitle: string;
  readonly dialogDescription: string;
  readonly confirmLabel: string;
  readonly toastTitle: string;
};

const DANGER_ACTIONS: readonly DangerAction[] = [
  {
    id: "transfer",
    title: "Transfer ownership",
    description: "Hand this workspace to another admin. You keep your member access.",
    buttonLabel: "Transfer",
    dialogTitle: "Transfer workspace ownership?",
    dialogDescription:
      "The new owner gains full billing and member control. You will be demoted to admin.",
    confirmLabel: "Transfer ownership",
    toastTitle: "Ownership transfer requested",
  },
  {
    id: "purge",
    title: "Delete all content",
    description: "Permanently remove every asset, draft, and scheduled post. Connections are kept.",
    buttonLabel: "Delete content",
    dialogTitle: "Delete all content?",
    dialogDescription:
      "This permanently deletes 128 assets and 6 scheduled posts. This cannot be undone.",
    confirmLabel: "Delete everything",
    toastTitle: "Content deletion scheduled",
  },
  {
    id: "delete",
    title: "Delete workspace",
    description: "Remove the workspace, its members, and all billing history.",
    buttonLabel: "Delete workspace",
    dialogTitle: "Delete this workspace?",
    dialogDescription:
      "All content, members, and connected accounts are permanently removed after a 30-day grace period.",
    confirmLabel: "Delete workspace",
    toastTitle: "Workspace deletion scheduled",
  },
];

export function DangerZoneSection(): React.JSX.Element {
  const { toast } = useToast();

  return (
    <SettingsSection
      id="danger-zone"
      title="Danger Zone"
      description="Irreversible actions that affect the entire workspace."
      isDestructive
    >
      <ul className="divide-y">
        {DANGER_ACTIONS.map((action) => (
          <li
            key={action.id}
            className="tablet:flex-row tablet:items-center tablet:justify-between flex flex-col gap-3 py-3.5 first:pt-0 last:pb-0"
          >
            <div className="min-w-0">
              <p className="text-sm font-semibold">{action.title}</p>
              <p className="text-muted-foreground mt-1 max-w-prose text-sm">{action.description}</p>
            </div>
            <ConfirmationDialog
              trigger={
                <Button variant="destructive" size="compact" className="shrink-0">
                  {action.buttonLabel}
                </Button>
              }
              title={action.dialogTitle}
              description={action.dialogDescription}
              confirmLabel={action.confirmLabel}
              isDestructive
              onConfirm={() => toast({ title: action.toastTitle })}
            />
          </li>
        ))}
      </ul>
    </SettingsSection>
  );
}
